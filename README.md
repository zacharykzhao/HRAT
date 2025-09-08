# HRAT

The README file is provided to help understand the code for HRAT (Structural Attack against Graph-based Android Malware Detection System, CCS'2021, Zhao, Kaifa and Zhou, Hao and Zhu, Yulin and Zhan, Xian and Zhou, Kai and Li, Jianfeng and Yu, Le and Yuan, Wei and Luo, Xiapu*). 



##### Requirements for using the Code

1. You need to use a Python 3.8+ environment that satisfies the following requirements:

```
numpy>=1.21.0,<2.0.0
scikit-learn>=1.0.0,<2.0.0
torch>=1.12.0,<3.0.0
torch-geometric>=2.0.0,<3.0.0
torchaudio>=0.12.0,<3.0.0
torchvision>=0.13.0,<2.0.0
scipy>=1.7.0,<2.0.0
tqdm>=4.60.0,<5.0.0
pandas>=1.3.0,<3.0.0
networkx>=2.6.0,<4.0.0
```

You can install these dependencies by running:
```bash
pip install -r requirements.txt
```

* A GPU version of PyTorch is recommended for better performance.

2. Java environment is required.

#### 1. Dataset

1. Malsan dataset
   1. Get the sha256 list for apps:
      1. https://sites.google.com/view/hrat/dataset-information
      2. Use the script (./DownloadAPK/downloadAPK.py) to download the dataset. Before that, please apply for the API key from AndroZoo (https://androzoo.uni.lu/) and replace the API key in line 9. Please follow the instructions in the script to correctly configure the variables to save downloaded APKs (line 34-37).
2. Obfuscated apps
   1. We use the dataset given in "S.Dong, M.Li, W.Diao, X.Liu, J.Liu, Z.Li, F.Xu, K.Chen, X.Wang, and K.Zhang. Understanding android obfuscation techniques: A large-scale investigation in the wild. In International conference on security and privacy in communication systems, pages 172–192. Springer, 2018." We ask for the permissions to access the dataset in this research. Please contact the first author to request access to the dataset. 



#### 2. Preprocess APKs

##### Step 1. Parse APKs

1. This step extracts function call graphs, node (method) lists and app methods constraints for each app. The source code for preprocessing APKs is given in the PreprocessAPK directory.

2. Users can also use the packaged jar file to preprocess APKs by:

   1. ```
      python3 PreprocessAPK.py --apk_path apk_file_path --output_path save_folder_path
      ```

      + Before running the aforementioned script, please make sure the "android_jars" (the files can be downloaded from https://drive.google.com/drive/folders/1CGEF_i5ss_pQ4uBq_jYr9MhxUIRGdHJz?usp=sharing) are correctly downloaded and located under the same path with PreprocessAPK.py
      + The APK files in the "apk_file_path" should be given in format of:
        + "apk_file_path/benign/*.apk"
        + "apk_file_path/malware/*.apk"
      + The "save_folder_path" will give the preprocessed results for each app in the following format:
        + "save_folder_path/benign/graph": gives the function call graphs for each app in "apk_file_path/benign/"
        + "save_folder_path/benign/nodes": gives the nodes list for each app in "apk_file_path/benign/"
        + "save_folder_path/benign/cons": gives the constraints for each node of apps in "apk_file_path/benign/"
        + "save_folder_path/malware/graph": gives the function call graphs for each app in "apk_file_path/malware/"
        + "save_folder_path/malware/nodes": gives the nodes list for each app in "apk_file_path/malware/"
        + "save_folder_path/malware/cons": gives the constraints for each node of apps in "apk_file_path/malware/"

##### Step 2. Format dataset

**Step 2.1. Translate function call graphs into adjacency matrix**

+ This step translates the function call graphs generated in Step 1, which are in format of "caller method signature ==> callee method signature" to adjacency matrix.

+ Please use the script "FCG2Adj.py" to achieve this. Replace the variables in line 37-38 to the path where you parsed APKs and the demo variable settings are given in line 41-43.

**Step 2.2. Format the adjacency matrix, combine label and sensitive API information for each app**

+ This step formats the adjacency matrix in the dataset into a unique file that includes the *adjacency matrix*, *label*, and sensitive API information for each app.
  + Please use the script "FormatData.py" to achieve this. Replace the variables in line 58-60 to the path where you parsed APKs and the demo variable settings are given in line 62-64.



#### 3. Attack Malscan

##### Step 1. Prepare training data and model

1. Train the model for Malscan and split the dataset into train and test datasets. Please use the script "./HRAT/AttackMalscan/getMalscanModel.py". Replace the variable in line 118 to the path where you saved the formatted data in "**Preprocess APKs/Step 2**".

##### Step 2. Evaluate HRAT on attacking Malscan

This step uses HRAT to modify the function call graph of malicious apps to escape detection of Malscan. Please run "./HRAT/AttackMalscan/main_malscan.py". Replace the path to train data, test data and constraints for each app in line 24-26.



#### 4. Attack Mamadroid

##### Step 1. Prepare training data and model 

1. **Step 1.1.** Get family index for each app. Run "./HRAT/AttackMamadroid/FormatDataforMamadroid.py". Replace the variables in line 33-36 with the path of node list of each app and the path to save the app's function index.
2. **Step 1.2.** Train the model for Mamadroid and split the dataset into train and test datasets. Please use the script "./HRAT/AttackMamadroid/getMamadroidModel.py". Replace the path to the formatted data for Mamadroid in step 1.1 in line 10.

##### Step 2. Evaluate HRAT on attacking Mamadroid

This step uses HRAT to modify the function call graph of malicious apps to escape detection of Mamadroid. Please run "./HRAT/AttackMamadroid/main_mamadroid.py", and replace the path to formatted train data, test data, constraints for each app, and path to save results in line 34-38.





#### 5. Attack APIGraph enhanced Malscan

##### Step 1. Format data for APIGraph enhanced Malscan

1. **Step 1.1.** Get APIGraph Android function cluster maps for each app. Run './HRAT/AttackAPIGraphMalscan/FormatAPIGraph.py'. Replace the path to parse app results (line 79) generated from *Preprocess APKs/Step 1. Parse APKs*.
2. **Step 1.2.** Split the dataset into train and test datasets for APIGraph enhanced Malscan. Please run "./HRAT/AttackAPIGraphMalscan/GetAPIGraphMalscanModel.py", and replace the path to the folder of each app's adjacency matrix, node list, node relation (generated by step 1.1) and the path to each app's node constraints path (line 29-32).

##### Step 2. Evaluate HRAT on attacking APIGraph enhanced Malscan

This step uses HRAT to modify the function call graph of malicious apps to escape detection of APIGraph enhanced Malscan. Please run "./HRAT/AttackAPIGraphMalscan/main_APIGraph_Malscan.py". Replace the path to formulated train data, test data, constraints for each app, path to node map for APIGraph and path to save results in line 24-28.



#### 6. APPMod

1. After evaluating HRAT on attacking different AMDs, you will get a list of app modification sequence on app's adjacency matrix. Then, you can use the script to translate the graph modification sequence to app function modification sequence. Please modify the path to graph modification sequence generated by HRAT in line 87, and the path to app node (line 88), the path to app graph (line 89) and the path to save app methods modification sequence.
2. To manipulate malware and generate adversarial apps with reference to app modification sequence, please run "./APPMOD/GraphMSeq_FuncMSeq.py". Replace the variable to path to app modification sequence (line 4), path to raw malware (line 5) and path to save adversarial apps. Before that, please make sure that "android_jars" (the files can be downloaded from https://drive.google.com/drive/folders/1CGEF_i5ss_pQ4uBq_jYr9MhxUIRGdHJz?usp=sharing) are correctly downloaded and located under the same path with PreprocessAPK.py
3. The source code for APPMod can be found at './APPMOD/FCGModification'. 






## Important Note

Please note that there is some randomness in the code, such as random selection of the first operation in HRAT, random initialization of the parameters of the DQN model in HRAT, and parameter initialization of the model when evaluating the original model. Therefore, when you evaluate experiments using our tools, the effect may be slightly different from the one provided.

## Citation

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
