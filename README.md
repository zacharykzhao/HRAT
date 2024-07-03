# HRAT



The READEME file is provided to help understand the code for HRAT (Structural Attack against Graph-based Android Malware Detection System, CCS'2021, Zhao, Kaifa and Zhou, Hao and Zhu, Yulin and Zhan, Xian and Zhou, Kai and Li, Jianfeng and Yu, Le and Yuan, Wei and Luo, Xiapu* ). 



##### Requirements for using the Code

1. You need to use a python 3 environment that satisfies the following requirements:

```
numpy==1.19.5
torch==1.8.0+cu111
torch-geometric==1.6.3
torchaudio==0.8.0
torchvision==0.9.0+cu111
tqdm==4.59.0
sklearn~=0.0
scikit-learn~=0.24.2
scipy~=1.5.2
tqdm~=4.63.0
pandas~=1.1.5
networkx~=2.5.1
```

* A GPU version pytorch is recommended.

2. Java environment are required.

#### 1. Dataset

1. Malsan dataset
   1. Get the sha256 list for apps:
      1. https://sites.google.com/view/hrat/dataset-informatin
      2. Use the script (./DownloadAPK/downloadAPK.py) to download the dataset, before that please apply for the APIKey from AndroZoo (https://androzoo.uni.lu/)  and replace the APIKey in line 9. Please follow the intructions in the script to correctly config she variables to save downloaded apks (line 34-37).
2. Obfuscated apps
   1. We use the dataset given in "S.Dong,M.Li,W.Diao,XLiu,J.Liu,Z.Li,F.Xu,K.Chen,X.Wang,andK.Zhang. Understanding android obfuscation techniques: A large-scale investigation in the wild. In International conference on security and privacy in communication systems, pages 172–192. Springer, 2018." We ask for the permissions to access the dataset in this research. Please contact the first author to request access to the dataset. 



#### 2. Preprocess APKs

##### Step1. Parse APKs

1. This step extracts function call graphs, node (method) lists and app methods constraints for each app. The source code for preprocessing apks is given in "".

2. The users can also use the packaged jar file to preprocess apks by:

   1. ```
      python3 PreprocessAPK.py --apk_path apk_file_path --output_path save_folder_path
      ```

      + Before running the aforementioned script, please make sure the "android_jars"   (the files can be downloaded from https://drive.google.com/drive/folders/1CGEF_i5ss_pQ4uBq_jYr9MhxUIRGdHJz?usp=sharing) are correctly downloaded and located under the same path with PrepreoecssAPK.py
      + The apks files in the "apk_file_path" should be given in format of:
        + "apk_file_path/benign/*.apk"
        + "apk_file_path/malware/*.apk"
      + The "save_folder_path" will give the preprocessed results for each app and given in format of :
        + "save_folder_path/benign/graph": gives the function call graphs for each app in "apk_file_path/benign/"
        + "save_folder_path/benign/nodes": gives the nodes list for  each app in "apk_file_path/benign/"
        + "save_folder_path/benign/cons": gives the constraints for each nodes of apps given in "apk_file_path/benign/"
        + "save_folder_path/malware/graph": gives the function call graphs for each app in "apk_file_path/malware/"
        + "save_folder_path/malware/nodes": gives the function call graphs for each app in "apk_file_path/malware/"
        + "save_folder_path/malware/cons": gives the constraints for each nodes of apps given in "apk_file_path/malware/"



##### Step2. Format dataset

Step 2.1.  Trasnlate function call graphs into adjacent matrix

+ This step translates the function call graphs generated in Step1, which are in format of "caller method signature ==> calle method signature" to adjacent matrix. 

+ Please use the script "FCG2Adj.py" to achieve this, replate the variables in line 37-38 to the path you parse apks and the demo variable settings are given in line 41-43.

Step 2.2. Format the adjacent matrix, combine label and sensitive api information for each app

+ This step format the adjacent matrix in the dataset into unique file that includes the *adjacent matrix*, *label*, and sensitive api information for each app.
  + Please use the script "FormatData.py" to achieve this, replate the variables in line 58-60 to the path you parse apks and the demo variable settings are given in line 62-64.



#### 3. Attack Malscan

##### Step 1. Prepare training data and model

1. Train the model for Malscan and split the data set into train and test dataset. Please use the script "./HRAT/AttackMalscan/getMalscanModel.py", replace the variable in line 118 to the path you save the formated data in "**Preprocess APKs/Step2**".

##### Step 2. Evaluate HRAT on attacking Malscan

This step use HRAT to modify the function call graph of malicious apps to escape detection of Malscan. Please run "./HRAT/AttackMalscan/main_malscan.py", replace the path to train data, test data and contraints for each app in line 24-26.



#### 4. Attack Mamadroid

##### Step 1. Prepare training data and model 

1. Step 1.1. Get family index for each app. Run "./HRAT/AttackMamadroid/FormatDataforMamadroid.py", replace the varibales in line 33-36 with the path of node list of each app and the path to save the apps function index.
2. Step 1.2. Train the model for Mamadroid and split the data set into train and test datset. Please use the script "./HRAT/AttackMamadroid/getMamadroidModel.py", replace the path to he formated data for mamdroid in step 1.1 in line 10.

##### Step 2. Evaluate HRAT on attacking Mamadroid

This step HRAT to modify the function call graph of malicious apps to escape detection of Mamadroid. Plesae run "./HRAT/AttackMamadroid/main_mamadroid.py", and replace the path to formated train data, test data, contraints for each app, and path to save results i line 34-38.





#### 5. Attack APIGraph enhanced Malscan

##### Step 1. Format data for APIGraph enhanced malscan

1.  Step 1.1. Get APIGraph Android function cluster maps for each app. Run './HRAT/AttackAPIGraphMalscan/FormatAPIGraph.py', replace the path to parse app results (line 79) generated from *Preprocess APKs/Step1. Parse APKs*.
2. Step 1.2. Split the data set into train and test dataset for APIGraph enhanced Malscan. Please run "./HRAT/AttackAPIGraphMalscan/GetAPIGraphMalscanModel.py", and repalce the path to the folder of each app's adjacent matrix, node list, node relation (generated by step 1.1) and the path to each app's node contraints  path (line 29-32).

##### Step 2. Evaluate HRAT on attacking APIGraph enhanced Malscan

This step HRAT to modify the function call graph of malicious apps to escape detection of APIGraph enhanced Mamadroid. Please run "./HRAT/AttackAPIGraphMalscan/main_APIGraph_Malscan.py", replace the path to formulated train data, test data, contraints for each app, path to node map for APIGraph and path to save results in line 24-28.



#### 6. APPMod

1. After evaluating HRAT on attacking different AMDs, you will get a list of app modification sequence on app's adjacent matrix. Then, you can use the script to transelate the graph modifacation sequence to app function modification sequence, please modify the path to graph modification sequence generated by HRAT in line 87, and the path to app node (Lin 88), the path to app graph (line 89) and the path to save app methods modification sequence.
2. To  manipulate malware and generate adversarial apps with reference to app modification sequence, please run "./APPMOD/GraphMSeq_FuncMSeq.py", replace the variable to path to app modification sequence (line 4), path to raw malware (line 5) and path to save adversarial apps. Before that, please make sure that "android_jars"   (the files can be downloaded from https://drive.google.com/drive/folders/1CGEF_i5ss_pQ4uBq_jYr9MhxUIRGdHJz?usp=sharing) are correctly downloaded and located under the same path with PrepreoecssAPK.py
3. The source code for APPMod can be found at './HRAT-main-2/APPMod/FCGModification'. 





##### Effectiveness Evaluation

To evaluate the effectiveness of HRAT, we evaluate HRAT on Malscan, Mamadroid and APIGraph enhanced Malscan with three settings. 

+ For Training using TRo and Testing using TEo, please download the dataset 'https://github.com/malscan-android/MalScan/tree/master/sha256/Malscan/11121314_benign.txt' and 'https://github.com/malscan-android/MalScan/tree/master/sha256/Malscan/11121314_malware.txt' to get the model and test data use the script described above;  
+ For Testing using TE1, please donwload the 'https://github.com/malscan-android/MalScan/tree/master/sha256/Malscan/2011_malware.txt' dataset to format the test data set; For Tesing using TE2, please donwload the 'https://github.com/malscan-android/MalScan/tree/master/sha256/Malscan/2012_malware.txt' dataset to format the test data set; 
+ For Training using TR2 and Testing using TE1, please use the dataset  'https://github.com/malscan-android/MalScan/tree/master/sha256/Malscan/2018_malware.txt' and  'https://github.com/malscan-android/MalScan/tree/master/sha256/Malscan/2018_benign.txt' for training and using 'https://github.com/malscan-android/MalScan/tree/master/sha256/Malscan/2011_malware.txt' dataset to format the test data set. 



##### Table 1 

- To reproduce Table 1, please run './HRAT/Results/Table1/ReproduceTable.py'. The users may need to download intermediate results with reference to the website provided in line 5. 
- To obtain Abs ASR, the authors can extract features based on the graphs and nodes provided in './HRAT/Results/Table1/advAPK' after the intermediate results are downloaded. 



##### Table 2

+ To reproduce Table 2, please run './HRAT/Results/Table2/ReproduceTable2.py'. The users may need to download intermediate results before run it.
  * Due to the long time and the renting of several different servers when doing this paper, some intermediate results of the HACK were lost. The statistical results of the paper have been provided in: "EA_Statistics.xlsx", which provides some statistical results of different EA algorithms.



##### Mdofication Efficiency Comparison

##### Table 3

- We provide our statistical results in './HRAT/Results/Table3/statistic_results.xlsx' this results can be obtained by manually conduct numerical statistic results provided in './HRAT/Results/Table3/Table3_Intermediate_results'/



#### Effectiveness of IMA

###### Figure 9

+ To generate Figure 9, please use matlab to run "./HRAT/Results/EfficiencyAnalysis/plot_efficiency_fig9.m". 



###### Figure 10

+ To generate Figure 10, please use matlab to run "./HRAT/Results/EfficiencyAnalysis/plot_action_ratio_fig10.m". 
+ 

#### Resilience to Obfuscation Techiniques

###### Table 4

- We provide our statistical results in '.HRAT/Results/Table4/statistic_results.xlsx' this results can be obtained by manually conduct numerical statistic results provided in '.HRAT/Results/Table4/Obfuscated_apk_modification_sequence/apk' and './HRAT/Results/Table4/Obfuscated_apk_modification_sequence/FeatureSpaceAttack'

  

##### Fnnctional Consistency Assessment

- The users can use the script to use monkey to automatic test adversarial apps. Before that, please make sure the adversarial apps generated by our tool are signed correctly. Make sure you have ADB (Android Debug Bridge) installed and properly set up and you have access to an Android device or emulator.
- Due to the long time and the renting of several different servers when doing this paper, some intermediate results of the HACK were lost.



#### Defense against HRAT

##### Evaluation

The code for evaluate defense strategies against hrat can be found in "./HRAT/Defense", i.e., retraining strategy ("./HRAT/Defense/retrain") and esemble learning ("./HRAT/Defense/ensemble_learning").



##### Figure 11

- Due to the long time and the renting of several different servers when doing this paper, some intermediate results of the HACK were lost. The statistical results for Figure 11 when finishing this manuscript have been provided in: "HRAT/Results/Figure11/StatisticalResults.xlsx", which provides statistical results of evaluating retraining to defense against HRAT.



- 

##### Appendix

##### FigTable 5 -- Evaluate Ensemble learning to defense against HRAT. 

- The intermediate results for the table are missing. The code to reproduce the results are provided in './HRAT/Defense/ensemble_learning'.



###### Fig 12 Effectiveness of HRAT over malware that fails to escape detection under individual attack action

+ To generate Figure 13, please use matlab to run "HRAT/Results/Figure12/plot_fig12.m", we munally conduct numerical statistical analysis on the intermediate results provided in './HRAT/Results/Figure12/action_ratio' to generate the figure.



###### Figure 13 Parameter analysis 

To generate Figure 13, please use matlab to run "HRAT/Results/ParameterAnalysis/plot_parameter_robustness_fig13.m". 







*** Please note that there is some randomness in the code, such as random selection of the first operation in HRAT, random initialization of the parameters of the DQN model in HRAT, and parameter initialization of the model when evaluating the original model. Therefore, when you evaluate experiments using our tools, the effect may be slightly different from the one provided.



If you end up building on this research or code as part of a project or publication, please include a reference to the ACM CCS paper:

```
@inproceedings{zhao2021structural,
author = {Zhao, Kaifa and Zhou, Hao and Zhu, Yulin and Zhan, Xian and Zhou, Kai and Li, Jianfeng and Yu, Le and Yuan, Wei and Luo, Xiapu},
title = {Structural Attack against Graph Based Android Malware Detection},
year = {2021},
isbn = {9781450384544},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3460120.3485387},
doi = {10.1145/3460120.3485387},
pages = {3218–3235},
numpages = {18},
keywords = {function call graph, android malware detection, structural attack},
location = {Virtual Event, Republic of Korea},
series = {CCS '21}
}
```