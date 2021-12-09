## how to run the code
1. build the project
2. Copy *android.jar* to the *./android_jars/android-\**
   1. you can also modify the android_jars path in *ZacharyKz/Config.java*
   2. public static String platformPath = "your_android_jars_path"; 
3. modify the code in *ZacharyKz/mainModification*
   1. use the code in * // for test *
   2. you can replace the sha256 with apks in * demo *
4. run the code *ZacharyKz/mainModification* 
5. remember to sign the repackages apk for test

## input files to the demo
1. the original Andorid app
   1. *demo/sha256.apk*
   2. The modification sequence: *demo/sha256_modifyGraph_attackseq.txt*
      1. each line is the modification action in the following format:
      ```
      add_node,:caller_signature ==> the node index of inserted node
      add_edge,:caller_signature ==> callee_signature
      delete_node,:target_node_signature
      delete_edge,:caller_signature ==> callee_signature ==> mid_method_signature
      ```