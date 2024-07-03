import subprocess
import time

def run_monkey_test(package_name, log_save_file, test_duration=1200, throttle=300):
    num_events = int(test_duration * 1000 / throttle)
    monkey_command = [
        "adb", "shell", "monkey",
        "-p", package_name,
        "--throttle", str(throttle),
        "--ignore-crashes",
        "--ignore-timeouts",
        "-v", str(num_events)
    ]

    process = subprocess.Popen(monkey_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()

    with open(log_save_file, "w") as log_file:
        log_file.write(out.decode())

    print("Monkey test completed and log saved.")

if __name__ == '__main__':

    apk_package_name = "com.example"
    log_save_file = apk_package_name + '_monkey_log.txt'
    run_monkey_test(apk_package_name,log_save_file)