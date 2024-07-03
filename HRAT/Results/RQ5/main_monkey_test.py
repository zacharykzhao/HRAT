import os
import subprocess

# your aapt path
aapt_path = './aapt'

# monkey parameters
event_delay = 300  # delay foe event/ms
test_duration = 20 * 60 * 1000  # test duration/ms
event_count = test_duration // event_delay  # event num
monkey_params = ' --throttle ' + str(event_delay) + ' --ignore-crashes --ignore-timeouts -v -v -v ' + str(event_count)

if __name__ == '__main__':
    raw_apk_path = './raw_apk'
    adv_apk_path = './signed_apk'
    log_path = './logs'
    if not os.path.exists(log_path): os.mkdir(log_path)

    for apk_sha256 in os.listdir(adv_apk_path):
        if apk_sha256.endswith('.apk'):
            app_apks = [os.path.join(raw_apk_path, apk_sha256),
                        os.path.join(adv_apk_path, apk_sha256)]
            sha256 = apk_sha256.split('.')[0]
            log_file_names = [os.path.join(log_path, sha256 + 'adv.log'),
                              os.path.join(log_path, sha256 + 'raw.log')]
            if os.path.exists(log_file_names[0]): continue
            for i in range(len(app_apks)):
                # adb commend to install app
                print('adb install ' + app_apks[i])
                install_cmd = 'adb install ' + app_apks[i]
                #
                subprocess.run(install_cmd, shell=True)

                # get package name
                # package_name_cmd = aapt_path + " dump badging " + app_apks[i] + " | awk '/package/{gsub(\"name=|'\",\"\", $2); print $2}'"
                package_name_cmd = aapt_path + ' dump badging ' + app_apks[
                    i] + ' | awk \'/package/{gsub("name=","",$2); print $2}\''
                package_name = subprocess.check_output(package_name_cmd, shell=True).decode('utf-8').strip()

                # 构建Monkey测试的adb命令
                monkey_cmd = 'adb shell monkey -p ' + package_name + monkey_params

                # save log
                with open(log_file_names[i], 'w') as log_file:
                    #
                    subprocess.run(monkey_cmd, shell=True, stdout=log_file)

                print('Monkey test for ' + package_name + ' is done. Log is saved in ' + log_file_names[i] + '.')
                # uninstall app
                uninstall_cmd = 'adb uninstall ' + package_name

                #
                subprocess.run(uninstall_cmd, shell=True)

                print('App ' + package_name + ' is uninstalled.')
