

clear
%%

file = dir("Action_ratio");



alg_name = {};
data = [];

for i = 3:size(file,1)
    file_name = "Action_ratio/"+file(i).name;
    tmp1 = readtable(file_name);
    data_tmp = tmp1{2:end, 2:end};
    add_edge = 0;
    rewiring = 0;
    add_node = 0;
    delete_node = 0;
    alg_name = [alg_name;file(i).name];

    data_tmpz = [];
    for z1 = 1:size(data_tmp,1)
        tt = data_tmp(z1,:);
        tmp = zeros(1,4);
        if tt(2) > 0
            tmp(1) = 1;
        end
        if tt(3) > 0       
            tmp(2) = 1;
        end
        if tt(4)>0
            tmp(3) = 1;    
        end
        if tt(5) > 0
            tmp(4) = 1;
        end
        data_tmpz = [data_tmpz;tmp];   
    end 
    data = [data; size(data_tmpz,1),sum(data_tmpz)];    
end

x = [];
y = [];
r = [];

for i = 1:size(data,1)
    x = [x, i * ones(1,4)];
    y = [y,1:4];
    tmp = data(i,:);
%     r = [r, tmp(2:5)/tmp(1)];
    r = [r, tmp(2:5)/sum( tmp(2:5))];
end


c = r;
scatter(x,y,r*10000,c,'filled')
y_name = ["add edge", "rewiring", "add node", "delete node"];
set(gca, 'XLim', [0, size(data,1)+1], 'XTick', 0:1:size(data,1)+1,...
    'YLim',[0,5], 'YTick', 0:1:5);
yticklabels(["","Add edge", "Rewiring", "Add node", "Delete node",""]);
xtl = {"", alg_name{1},alg_name{2},    alg_name{3},alg_name{4},     alg_name{5},alg_name{6},    alg_name{7},alg_name{8},""};
set(gca,'FontSize',12)
for i = 1:size(xtl,2)
    
    tmp = string(xtl{i});
    tmp = tmp.replace("_","\_");
    tmp = tmp.replace(".csv","");
    xtl{i} = tmp ;
end
xticklabels(xtl)
xtickangle(25)


% colormap(gca,'bone')
% mesh(peaks)
colormap(othercolor('PuBu3'))
dx = -0.3;
dy = 0;
text(x+dx, y+dy, trans_double_str(r),'FontSize',12, 'FontWeight','bold');
