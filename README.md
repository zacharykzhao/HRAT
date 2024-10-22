# HRAT
[Structural Attack against Graph-based Android Malware Detection System](https://dl.acm.org/doi/abs/10.1145/3460120.3485387)




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



## Installation

Before getting started, we recommend setting up a Python 3(>=3.6.12) virtual environment. For APPMod (Android Application Manipulation Tool in our paper,), ensure you have installed a Java SDK >= 1.8.0_282.





Because our APK parsing process (extracting function call graphs, node lists and node constraints) and APK manipulation process are based on Java and function call modification process is based on 



+ Step 1: Extract function graph, node lists and node constraints from APK files:

  + ```python
    python3 PreprocessAPK.py --apk_path apk_file_path -- output_path save_folder_path
    ```

  + before that please include 'android_jars' under current folder: 

  + please download the *PreprocessAPK.jar* from: https://drive.google.com/drive/folders/1CGEF_i5ss_pQ4uBq_jYr9MhxUIRGdHJz?usp=sharing  , and put it under *./libs*

  + The Java source code of APK preprocess can be found under: */APPMod/PreprocessAPK*


