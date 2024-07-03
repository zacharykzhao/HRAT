clear
clc
close all
%%
root_path = ".\parameter_fig10";
algorithms = ["malscan", "mamadroid"];
parameter_name = ["memory_capacity", "probability"];

accuracy = [];
avg_mod =[];

for za = 1:2
    alg = algorithms(za);
    for zp = 1:2
        pn = parameter_name(zp);
        result_path = root_path + "\" + alg + "\" + pn;
        result_files = dir(result_path);
        avg_mod_tmp = [];
        acc_tmp = [];
        for zrf = 3:size(result_files)
            file_name = result_path + "\" + result_files(zrf).name;
            data_tmp = importdata(file_name);
            data_tmp = data_tmp.data;
            avg_mod_tmp = [avg_mod_tmp, sum(data_tmp(:,1))/size(data_tmp,1)];
            acc_tmp = [acc_tmp, size(data_tmp,1)/502];
        end              
        accuracy = [accuracy; acc_tmp];
        avg_mod = [avg_mod;avg_mod_tmp];
    end  
end
%%


mem_acc = accuracy([1,3],:);
mem_avg = avg_mod([1,3],:);

prob_acc = accuracy([2,4],:);
prob_avg = avg_mod([2,4],:);

tiledlayout(2,2)

%% plot memory capacity 
x = 1:4;
ax1 = nexttile;

% yyaxis left
plot(x, mem_acc(1,:),'g-s', x, mem_acc(2,:),'b--o', 'LineWidth',1)

lgd.Layout.Tile = 'east';

xlim([0.5,4.5])
xticks([0, 1,2,3,4,5])
xticklabels({'','1','5','10','30',''})
ylim([0.7 1.1])
yticks([0.8,0.9, 1])
yticklabels(["80%","90%","100%"])

xlabel("Memory capacity")
ylabel("ASR")
% set('LineWidth', 2)
set(gca,'FontSize',12, 'LineWidth',1, 'YGrid','on')


%% plot
% figure
ax2 = nexttile;
x = 1:4;
plot(x, prob_acc(1,:),'g-s', x, prob_acc(2,:),'b--o', 'LineWidth',1)

legend("malscan", "mamadroid")
xlim([0.5,4.5])
xticks([0, 1,2,3,4,5])
xticklabels({'','80%','85%','90%','95%',''})
xlabel("Probability")
ylabel("ASR")
ylim([0.7 1.1])
yticks([0.8,0.9, 1])
yticklabels(["80%","90%","100%"])
set(gca,'FontSize',12, 'LineWidth',1, 'YGrid','on')

%% plot
% figure
ax2 = nexttile;
x = 1:4;
plot(x, mem_avg(1,:),'g-s', x, mem_avg(2,:),'b--o', 'LineWidth',1)

xlim([0.5,4.5])
xticks([0, 1,2,3,4,5])
xticklabels({'','1','5','10','30',''})
xlabel("Memory capacity")
ylabel("Avg. Mod")
ylim([10 45])
set(gca,'FontSize',12, 'LineWidth',1, 'YGrid','on')

%% plot
% figure
ax2 = nexttile;
x = 1:4;
plot(x, prob_avg(1,:),'g-s', x, prob_avg(2,:),'b--o', 'LineWidth',1)
xlim([0.5,4.5])
xticks([0, 1,2,3,4,5])
xticklabels({'','80%','85%','90%','95%',''})
xlabel("Probability")
ylabel("Avg. Mod")
ylim([10 30])
set(gca,'FontSize',12, 'LineWidth',1, 'YGrid','on')







