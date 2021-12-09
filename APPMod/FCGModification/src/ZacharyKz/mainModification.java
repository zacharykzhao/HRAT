package ZacharyKz;

import soot.*;
import soot.javaToJimple.LocalGenerator;
import soot.jimple.*;
import soot.jimple.infoflow.android.manifest.ProcessManifest;
import soot.jimple.toolkits.callgraph.CallGraph;
import soot.jimple.toolkits.callgraph.Edge;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import static ZacharyKz.FileUtils.readFile;
import static ZacharyKz.ModificationUtils.*;

public class mainModification {
    public static void main(String[] args) throws Exception {
        String sha256 = args[0];
        String outputPath = args[1];
        String save_path = args[2];
        String apk_path_sub = args[3];
        String seq_sequence = args[4];
        String attacked_graph = seq_sequence + "/" + sha256 + "_modifyGraph_attackseq.txt";
        String apk_path = apk_path_sub + "/" + sha256 + ".apk";

//        // for test
//         sha256 = "8E95B69DD5551E72CB1CD8570B4D369044E4710A31020C7AC8F3587C1D316B0C";
//         apk_path = "./demo/" + sha256 + ".apk";
//         attacked_graph = "./demo/"+ sha256+"_modifyGraph_attackseq.txt";
//         outputPath = "demo_results";
//         save_path = "demo_results";

        //
        System.out.println(sha256);
        ProcessManifest manifest = null;
        //
        SootEnvironment.init(apk_path, "android_jars", outputPath);
        CallGraph cg = Scene.v().getCallGraph(); // debug
        HashMap<String, HashMap<String, HashSet<String>>> dataCg = new HashMap<>();
        for (Edge edge : cg) {
            if (edge.src().getDeclaringClass().getName().equals("dummyMainClass")) {
                continue;
            }
            if (edge.srcStmt() == null) {
                continue;
            }
//                System.out.println(edge);
            String caller_sig = edge.src().toString();
            String cor_stmt = edge.srcStmt().toString();
            String callee_sig = edge.tgt().toString();
            if (!dataCg.containsKey(caller_sig)) {
                dataCg.put(caller_sig, new HashMap<String, HashSet<String>>());
            }
            if (!dataCg.get(caller_sig).containsKey(cor_stmt)) {
                dataCg.get(caller_sig).put(cor_stmt, new HashSet<String>());
            }
            dataCg.get(caller_sig).get(cor_stmt).add(callee_sig);
        }
        //
        if (cg != null) {

            String data = readFile(attacked_graph);
            String[] call_relation = data.split("\n");
            System.out.println("Call Graph Extracted! \n");
            // initialate
            ProcessManifest processManifest = new ProcessManifest(apk_path);
            SootClass MidType = createMidType(processManifest);
            String apkPackageName = processManifest.getPackageName();
            //
            HashMap<String, List<String>> sigBufAdd = new HashMap<>();
            HashMap<String, List<String>> sigBufMid = new HashMap<>();
            //
            for (int z1 = 0; z1 < call_relation.length; z1++) {
                String tmp = call_relation[z1];
                String attackType = tmp.split(",:")[0];
                System.out.println(tmp);
                if (attackType.equals("add_edge")) {
                    String caller_signature = tmp.split(",:")[1].split(" ==> ")[0];
                    String callee_signature = tmp.split(",:")[1].split(" ==> ")[1];

                    if (caller_signature.length() <= 3) {
//                            caller_signature = "<"+apkPackageName+".zkfclass: int zkf" + caller_signature + "()>";
                        caller_signature = "zkf" + caller_signature;
                        caller_signature = getNewestSignature(caller_signature, sigBufAdd, sigBufMid);
                    }
                    if (callee_signature.length() <= 3) {
//                            callee_signature = "<"+apkPackageName+".zkfclass: int zkf" + callee_signature + "()>";
                        callee_signature = "zkf" + callee_signature;
                        callee_signature = getNewestSignature(callee_signature, sigBufAdd, sigBufMid);
                    }
                    add_edge(caller_signature, callee_signature, dataCg, sigBufAdd, sigBufMid);
                } else if (attackType.equals("delete_edge")) {
                    String A_signature = tmp.split(",:")[1].split(" ==> ")[0];
                    String B_signature = tmp.split(",:")[1].split(" ==> ")[1];
                    String C_signature = tmp.split(",:")[1].split(" ==> ")[2];
                    if (A_signature.length() <= 3) {
//                            A_signature = "<"+apkPackageName+".zkfclass: int zkf" + A_signature + "()>";
                        A_signature = "zkf" + A_signature;
                        A_signature = getNewestSignature(A_signature, sigBufAdd, sigBufMid);
                    }
                    if (B_signature.length() <= 3) {
//                            B_signature = "<"+apkPackageName+".zkfclass: int zkf" + B_signature + "()>";
                        B_signature = "zkf" + B_signature;
                        B_signature = getNewestSignature(B_signature, sigBufAdd, sigBufMid);
                    }
                    if (C_signature.length() <= 3) {
//                            C_signature = "<"+apkPackageName+".zkfclass: int zkf" + C_signature + "()>";
                        C_signature = "zkf" + C_signature;
                        C_signature = getNewestSignature(C_signature, sigBufAdd, sigBufMid);
                    }
                    rewiring(A_signature, B_signature, C_signature,
                            MidType, sigBufAdd, sigBufMid, processManifest);

                } else if (attackType.equals("add_node")) {
                    String method_sig = tmp.split(",:")[1];
                    String caller_signature = null, callee_signature = null;
                    SootMethod caller_method = null;
                    String className = null;
                    if (method_sig.split(" ==> ").length == 2) {
                        caller_signature = tmp.split(",:")[1].split(" ==> ")[0];
                        callee_signature = tmp.split(",:")[1].split(" ==> ")[1];
                        if (caller_signature.length() <= 3) {
//                            caller_signature = "<"+apkPackageName+".zkfclass: int zkf" + caller_signature + "()>";
                            caller_signature = "<" + apkPackageName + ".zkfclass: int zkf" + caller_signature + "()>";
                        }
                        if (callee_signature.length() <= 3) {
//                            callee_signature = "<zkfclass: int zkfclassf" + callee_signature + "()>";
                            callee_signature = "zkf" + callee_signature;
                        }
                        className = apkPackageName + ".zkfclass";
                    } else if (method_sig.split(" ==> ").length == 3) {
                        caller_signature = tmp.split(",:")[1].split(" ==> ")[0];
                        callee_signature = tmp.split(",:")[1].split(" ==> ")[1];
                        String state_name = tmp.split(",:")[1].split(" ==> ")[2];
                        callee_signature = "zkf" + callee_signature;
                        if (caller_signature.length() <= 3) {
                            caller_signature = "zkf" + caller_signature;
                        }
                        if (state_name.equals("obfuscated")) {
                            className = "a.b.c";
                        } else if (state_name.equals("selfdefined")) {
                            className = apkPackageName + ".zkfclass";
                        } else {
                            className = state_name + "zkfclass";
                        }
                    }
                    caller_signature = getNewestSignature(caller_signature, sigBufAdd, sigBufMid);
                    callee_signature = getNewestSignature(callee_signature, sigBufAdd, sigBufMid);
                    caller_method = Scene.v().getMethod(caller_signature);
                    SootMethod nm = insert_new_nodes(caller_method, apkPackageName, className, callee_signature);
                    List<String> sigTemp = null;
                    if (sigBufAdd.containsKey(callee_signature)) {
                        sigTemp = sigBufAdd.get(callee_signature);
                    } else {
                        sigTemp = new ArrayList<>();
                    }
                    sigTemp.add(nm.getSignature());
                    sigBufAdd.put(callee_signature, sigTemp);
                    // System.out.println("\t" +nm.getSignature());
                } else if (attackType.equals("delete_node")) {
                    String nodeSignature = tmp.split(",:")[1];

                    if (nodeSignature.length() <= 3) {
                        nodeSignature = "zkf" + nodeSignature;
                    }
                    nodeSignature = getNewestSignature(nodeSignature, sigBufAdd, sigBufMid);

                    SootMethod sootMethod = Scene.v().getMethod(nodeSignature);
                    System.out.println("deleting:" + nodeSignature);
                    remove_nodes(sootMethod, nodeSignature);
                }

            }
            PackManager.v().writeOutput();
            getGraphNodesSha256(sha256, outputPath, save_path);
            System.out.println(sha256);
        }
    }

}
