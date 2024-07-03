%% ori dat
%%
% Target	alg
% Malscan 	Add edge	0.375		35.9047619
% 	Rewiring	0.34431631		37.53110048
% 	Insert node	0.283625731		24.20618557
% 	Delete node	0.303983229		6.620689655
% 	Add edge	0.875		1
% APIGraph	Rewiring	0.964285714		1
% 	Insert node	0.891891892		1
% 	Delete node	0.944444444		1
% Mamadroid	Add edge	1		9.127939142
% 	Rewiring	1		9.527355623
% 	Insert node	0.999267399		9.147877013
% 	Delete node	1		9.118503119


%%
% x = [1980 1990 2000];
% y = [40 50 63 52; 42 55 50 48; 30 20 44 40];
% barh(x,y)
% xlabel('Snowfall')
% ylabel('Year')
% legend({'Springfield','Fairview','Bristol','Jamesville'})
clear
clc
x = [1,2,3];
y = [0.875	0.964285714	0.891891892	0.944444444; 
    1	1	0.999267399	1
     0.375	0.838550247	0.868421053	0.932914046
 ];
barh(x,y)

xlim([0  1.3])
legend({'Add edge', 'Rewiring', 'Insert node', 'Delete node'})
dx=0;
dy=0;

z =reshape(y', 1,12);


xidx = reshape(y',1,12);
yidx = []
for i = 1:3
   for j = 0.15:0.15:0.7 
    yidx = [yidx, i-0.3+j];
   end
end
xtl = '\begin{tabular}{c} APIGraph \\ +Malscan\end{tabular}'
yticklabels({'APIGraph', 'Mamadroid','Malscan'})
% set(gca,'yticklabel',{{'line1','line2'}}) 

xlabel('Ratio')
text(xidx, yidx, trans_double_str(z));
