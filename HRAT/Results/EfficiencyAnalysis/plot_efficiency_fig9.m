% clear
%%
% 画 EA的efficiency graph

%%
close all
efficiency_dir = ".\efficiency_fig9";
files = dir(efficiency_dir);

line_style = ['x','o', '>', 'h','<'];

alg_names = [];

count = 1;
for i = 3:size(files,1)

    hold on
    alg = split(files(i).name,".");
    if string(alg(1)).contains('API')
        continue
    end
    alg_names = [alg_names, replace(alg(1),"_", " ")];
    file_name = efficiency_dir+"\"+files(i).name;
    data_tmp = importdata(file_name);
    data_tmp = data_tmp.data;
    h = cdfplot(data_tmp(:,1));
    
    set(h,'Marker', line_style(count),'LineWidth', 1)
    count = count + 1;
end

legend(alg_names(1,:))
xlim([0 300])
% ylim([0.5 1])
xlabel('No. of escaping modifications')
ylabel('CDF')
set(gca, 'BoxStyle', 'full','FontSize', 12)