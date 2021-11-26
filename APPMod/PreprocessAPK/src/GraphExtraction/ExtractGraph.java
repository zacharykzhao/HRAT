package GraphExtraction;


import soot.*;
import soot.jimple.CaughtExceptionRef;
import soot.jimple.IdentityStmt;
import soot.jimple.infoflow.android.manifest.ProcessManifest;
import soot.jimple.infoflow.cmd.Flowdroid;
import soot.jimple.infoflow.memory.FlowDroidTimeoutWatcher;
import soot.jimple.infoflow.results.InfoflowResults;
import soot.jimple.toolkits.callgraph.CallGraph;
import soot.jimple.toolkits.callgraph.Edge;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class ExtractGraph {
    public static String[] framework = {"java.", "sun.", "android.", "org.apache.", "org.eclipse.", "soot.", "javax.",
            "com.google.", "org.xml.", "junit.", "org.json.", "org.w3c.com"};
    public static String[] lifecycle = {"onCreate", "onClick", "onStart", "onResume", "onPause", "onStop", "onRestart", "onDestroy"};


    public static void main(String[] args) {
        /**
         * input:
         *     1. apk file: full path of apk_file
         *     2. save_path: save path of extracted graph, nodes list, constraints list
         * **/
        String apk_file = args[0];
        String save_path = args[1];

//        String apk_file = "F:/apk/1112/benign/1A549F682456D6EF5B6F8444CD50A88B06DD1623973B3C6EE29DACB129D3A740.apk";
//        String save_path = "F:/todelete2021_11_17";

        String[] tmp = apk_file.split("/");
        String sha256 = tmp[tmp.length - 1].split("\\.")[0];
        String node_save_path = save_path + "/nodes";
        String graph_save_path = save_path + "/graph";
        String cons_save_path = save_path + "/cons";
        checkFolder(node_save_path);
        checkFolder(graph_save_path);
        checkFolder(cons_save_path);
        //
        System.out.println(sha256);
        //
        String node_file = node_save_path + "/" + sha256 + ".txt";
        String graph_file = graph_save_path + "/" + sha256 + ".txt";
        String cons_file = cons_save_path + "/" + sha256 + ".txt";
        File file11 = new File(node_file);
        if (file11.exists()) {
            System.out.println("exit");
            return;
        }
        extractGraphNodesCons(apk_file, graph_file,
                node_file, cons_file);

    }

    private static void extractGraphNodesCons(String apk_file,
                                              String graph_save_file,
                                              String node_save_file,
                                              String cons_save_file) {
        ProcessManifest manifest = null;
        try {
            // -- set up FlowDroid environment
            // SootEnvironment.init(apk_path, Config.platformPath);
            FlowdroidEnvironment.reset();
            FlowdroidEnvironment.init(apk_file, Config.platformPath);
//            System.out.println("set timeoutFlag");
            // calculate timeout for FlowDroid
            FlowDroidTimeoutWatcher.timeoutFlag = false; // reset - *very important*
            int flowdroidArgsSize = FlowdroidEnvironment.args.size();
            String[] flowdroidArgs = new String[flowdroidArgsSize];
            FlowdroidEnvironment.args.toArray(flowdroidArgs);
            ArrayList<InfoflowResults> flowdroidResults = Flowdroid.analyze(flowdroidArgs);
            if (Flowdroid.exceptionFlag == true) {
                // System.out.println("---->>>> EXCEPTION");
                return;
            }
            manifest = new ProcessManifest(apk_file);
            String packageName = manifest.getPackageName();
            if (FlowDroidTimeoutWatcher.timeoutFlag == true) {
                // System.out.println("---->>>> TIMEOUT: " + durationFD);
                return;
            }
            CallGraph cg = Scene.v().getCallGraph();
//            System.out.println(cg);
            assert (cg != null);
            List<String> node = new ArrayList<>();
            List<Integer> constraints = new ArrayList<>();
            System.out.println("\t constructing graph");
            try (BufferedWriter writer = new BufferedWriter(
                    new FileWriter(
                            new File(graph_save_file)))
            ) {
                System.out.println("\t\tbegine write graph into file.");
                for (Edge edge : cg) {
                    if (edge.src().getDeclaringClass().getName().equals("dummyMainClass")) {
                        continue;
                    }
                    if (edge.tgt().getDeclaringClass().getName().equals("dummyMainClass")) {
                        continue;
                    }
                    writer.write(edge.getSrc().toString() + " ==> " + edge.getTgt().toString() + "\n");
                }
            } catch (IOException e) {
                e.printStackTrace();
                return;
            }

            // extract nodes and cons
            for (Edge edge : cg) {
                SootMethod src = edge.src();
                SootMethod tgt = edge.tgt();
                int srcFlag = 1;
                int tgtFlag = 1;

                // caller constraints
                String srcClassName = src.getDeclaringClass().getName();
                for (int z1 = 0; z1 < framework.length; z1++) {
                    if (srcClassName.startsWith(framework[z1])) {
                        srcFlag = 0;
                        if (node.contains(tgt.getSignature())) {
                            int idxTmp = node.indexOf(tgt.getSignature());
                            constraints.set(idxTmp, 0);
                        }
                        break;
                    }
                }
                String srcName = src.getName().toString();
                if (srcName.startsWith("on")) {
                    srcFlag = -2;
                }
                for (int z1 = 0; z1 < lifecycle.length; z1++) {
                    if (srcName.startsWith(lifecycle[z1])) {
                        srcFlag = 0;
                    }
                    break;
                }
                if (src.getSignature().toString().contains("<clinit>(") || src.getSignature().toString().contains("<init>(")) {
                    srcFlag = 0;
                }
                if (srcClassName.equals("dummyMainClass")) {
                    srcFlag = 0;
                    continue;
                }
                SootClass sootClass = Scene.v().getSootClass(srcClassName);
                List<SootMethod> methods = sootClass.getMethods();
                int srcInstantilizeFlag = 0;
                int srcttt = 0;
                for (SootMethod sootMethod : methods) {
                    if (sootMethod.getSignature().equals(src.getSignature())) {
                        srcttt = 1;
//                        break;
                    }
                    if (sootMethod.getName().contains("<init>")) {
                        if (sootMethod.getParameterCount() == 0) {
                            srcInstantilizeFlag = 1;
                        }
                    }
                    if (sootMethod.getName().contains("<clinit>")) {
                        if (sootMethod.getParameterCount() == 0) {
                            srcInstantilizeFlag = 1;
                        }
                    }
                }
                if (srcInstantilizeFlag == 0) {
                    srcFlag = 0;
                }
                if (srcttt == 0) {
                    srcFlag = 0;
//                    System.out.println("\t not soot method: " + src.getSignature());
                    if (node.contains(tgt.getSignature())) {
                        int idxTmp = node.indexOf(tgt.getSignature());
                        constraints.set(idxTmp, 0);
                    }
                }
                if (!src.isConcrete() || src.isPhantom()) {
                    srcFlag = 0;
                }
                try {
                    src.retrieveActiveBody();
                } catch (Exception e) {
                    srcFlag = 0;
                }
                if (srcFlag == 1) {
                    Body srcBody = src.retrieveActiveBody();
                    PatchingChain<Unit> units = srcBody.getUnits();
                    for (Unit unit : units) {
                        if (unit instanceof IdentityStmt) {
                            IdentityStmt stmt = (IdentityStmt) unit;
                            if (stmt.getRightOp() instanceof CaughtExceptionRef) {
                                srcFlag = 0;
                                break;
                            }
                        }
                    }
                }
                // callee constraints
                String tgtClassName = tgt.getDeclaringClass().getName();
                for (int z1 = 0; z1 < framework.length; z1++) {
                    if (tgtClassName.startsWith(framework[z1])) {
                        tgtFlag = 0;
                        break;
                    }
                }
                String tgtName = tgt.getName();
                for (int z1 = 0; z1 < lifecycle.length; z1++) {
                    if (tgtName.startsWith(lifecycle[z1])) {
                        tgtFlag = 0;
                    }
                    break;
                }
                if (tgt.getSignature().contains("<clinit>(") || tgt.getSignature().contains("<init>(")) {
                    tgtFlag = 0;
                }
                if (tgtClassName.equals("dummyMainClass")) {
                    continue;
                }
                if (!tgt.isConcrete() || src.isPhantom()) {
                    tgtFlag = 0;
                }
                SootClass tgtsootClass = Scene.v().getSootClass(tgtClassName);
                List<SootMethod> tgtmethods = tgtsootClass.getMethods();
                int tgtInstantilizeFlag = 0;
                int tgtttt = 0;
                for (SootMethod sootMethod : tgtmethods) {
                    if (sootMethod.getSignature().equals(tgt.getSignature())) {
                        tgtttt = 1;
//                        break;
                    }
                    if (sootMethod.getName().contains("<init>")) {
                        if (sootMethod.getParameterCount() == 0) {
                            tgtInstantilizeFlag = 1;
                        }
                    }
                    if (sootMethod.getName().contains("<clinit>")) {
                        if (sootMethod.getParameterCount() == 0) {
                            tgtInstantilizeFlag = 1;
                        }
                    }
                }
                if (tgtInstantilizeFlag == 0) {
                    tgtFlag = 0;
                }
                if (tgtttt == 0) {
                    tgtFlag = 0;
//                    System.out.println("\t not soot method: " + tgt.getSignature());
                }
                try {
                    tgt.retrieveActiveBody();
                } catch (Exception e) {
                    tgtFlag = 0;
                }
                if (tgtFlag == 1) {
                    Body tgtBody = tgt.retrieveActiveBody();
                    PatchingChain<Unit> tgtunits = tgtBody.getUnits();
                    for (Unit unit : tgtunits) {
                        if (unit instanceof IdentityStmt) {
                            IdentityStmt stmt = (IdentityStmt) unit;
                            if (stmt.getRightOp() instanceof CaughtExceptionRef) {
                                tgtFlag = 0;
                                break;
                            }

                        }
                    }
                }
//                System.out.println("src:" + srcFlag +" : "+ src.getSignature().toString() );
//                System.out.println("tgt:" + tgtFlag + " : " + tgt.getSignature().toString());
                if (!node.contains(src.getSignature())) {
                    node.add(src.getSignature());
                    constraints.add(srcFlag);
                }
                if (!node.contains(tgt.getSignature())) {
                    node.add(tgt.getSignature());
                    constraints.add(tgtFlag);
                }
            }
            assert (constraints.size() == node.size());
            int count0 = 0;
            for (int a : constraints) {
                if (a == 0) {
                    count0 += 1;
                }
            }
            System.out.println("\t writing cons");
            try (BufferedWriter writer = new BufferedWriter(
                    new FileWriter(
                            new File(cons_save_file)))
            ) {
//                System.out.println("\t\tbegine write nodes into file.");
                for (int z1 = 0; z1 < constraints.size(); z1++) {
                    writer.write(constraints.get(z1) + "\n");
                }
            }
            System.out.println("\t writing nodes");
            try (BufferedWriter writer = new BufferedWriter(
                    new FileWriter(
                            new File(node_save_file)))
            ) {
//                System.out.println("\t\tbegine write nodes into file.");
                for (int z1 = 0; z1 < node.size(); z1++) {
                    writer.write(node.get(z1) + "\n");
                }
            }
            System.out.println("\t\t number of modifiable nodes:" + (node.size() - count0) + "  cannot: " + count0);
            System.out.println("\t\t compare node " + node.size() + " ??? con " + constraints.size());
        } catch (IOException e) {
            e.printStackTrace();
            return;
        } catch (org.xmlpull.v1.XmlPullParserException e) {
            e.printStackTrace();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void checkFolder(String folerName) {
        File folder = new File(folerName);
        if (!folder.exists() && !folder.isDirectory()) {
            folder.mkdirs();
        }
    }
}
