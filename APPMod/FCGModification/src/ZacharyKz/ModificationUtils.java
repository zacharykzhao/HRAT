package ZacharyKz;

import soot.*;
import soot.javaToJimple.LocalGenerator;
import soot.jimple.*;
import soot.jimple.infoflow.android.manifest.ProcessManifest;
import soot.jimple.infoflow.cmd.Flowdroid;
import soot.jimple.infoflow.memory.FlowDroidTimeoutWatcher;
import soot.jimple.infoflow.results.InfoflowResults;
import soot.jimple.internal.*;
import soot.jimple.toolkits.callgraph.CallGraph;
import soot.jimple.toolkits.callgraph.Edge;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.*;

public class ModificationUtils {
    public static String[] framework = {"java.", "sun.", "android.", "org.apache.", "org.eclipse.", "soot.", "javax.",
            "com.google.", "org.xml.", "junit.", "org.json.", "org.w3c.com"};
    public static String[] lifecycle = {"onCreate", "onClick", "onStart", "onResume", "onPause", "onStop", "onRestart", "onDestroy"};

    //
    public static SootClass createMidType(ProcessManifest processManifest) {
        String apkPackage = processManifest.getPackageName();
        String className = apkPackage + ".MidType";
        SootClass sootClass = new SootClass(className, Modifier.PUBLIC);
        sootClass.setSuperclass(Scene.v().getSootClass("java.lang.Object"));
        sootClass.setApplicationClass();
        return sootClass;
    }

    public static String getNewestSignature(String ori_sig, HashMap<String, List<String>> sigBufAdd,
                                            HashMap<String, List<String>> sigBufMid) {
        String tmp_add = "";
        String tmp_mid = "";
        String sig = ori_sig;
        if (sigBufAdd.get(ori_sig) != null) {// method A has been modified, update the signature
            List<String> tmpzzz = sigBufAdd.get(ori_sig);
            tmp_add = tmpzzz.get(tmpzzz.size() - 1);
        }
        if (sigBufMid.get(ori_sig) != null) {// method A has been modified,
            List<String> tmpzzz = sigBufMid.get(ori_sig);
            tmp_mid = tmpzzz.get(tmpzzz.size() - 1);
        }
        if (tmp_add.length() > sig.length()) {
            sig = tmp_add;
        }
        if (tmp_mid.length() > sig.length()) {
            sig = tmp_mid;
        }
        return sig;
    }


    public static void add_edge(String caller_signature, String callee_signature,
                                HashMap<String, HashMap<String, HashSet<String>>> cg,
                                HashMap<String, List<String>> sigBufAdd,
                                HashMap<String, List<String>> sigBufMid) {
        //
        int added_FLAG = 0;
        String original_callee_signature = callee_signature;
        caller_signature = getNewestSignature(caller_signature, sigBufAdd, sigBufMid);
        String callee_tmp = "";
        callee_tmp = getNewestSignature(callee_signature, sigBufAdd, sigBufMid);
        if (sigBufAdd.get(callee_signature) != null) {// callee has been modified
            added_FLAG = 1;
        }
        if (!callee_tmp.equals(callee_signature)) {
            callee_signature = callee_tmp;
        }
        SootMethod newMethod = Scene.v().getMethod(callee_signature);

        String tar_pName = caller_signature.split(": ")[0];
        tar_pName = tar_pName.split("<")[1];
        SootClass caller_sClass = Scene.v().getSootClass(tar_pName);
        //
        String tmpCalleeCheck = callee_signature;
        int count_int = 1;
        if (tmpCalleeCheck.contains("()")) {
            tmpCalleeCheck = tmpCalleeCheck.replace(")>", "int)>");
        } else {
            tmpCalleeCheck = tmpCalleeCheck.replace(")>", ",int)>");
        }
        while (Scene.v().containsMethod(tmpCalleeCheck)) {
            tmpCalleeCheck = tmpCalleeCheck.replace(")>", ",int)>");
            count_int++;
        }
        SootMethod caller_sMethod = null;
        caller_sMethod = Scene.v().getMethod(caller_signature);
        if (caller_sMethod.isPhantom()) {
            throw new RuntimeException();
        }
        if (added_FLAG == 0) {
            String callee_class_name = callee_signature.split(": ")[0].split("<")[1];
            SootClass callee_sClass = Scene.v().getSootClass(callee_class_name);
            /*** replace method the same as callee, with added parameterrs ***/
            newMethod = replaceMethod(callee_signature, callee_sClass, count_int);
            // 更新signature， 如果原method被修改过，则利用最近最近修改的sig去寻改、修改该method
            List<String> sigTemp = null;
            if (sigBufAdd.containsKey(original_callee_signature)) {
                sigTemp = sigBufAdd.get(original_callee_signature);
            } else {
                sigTemp = new ArrayList<>();
            }
            sigTemp.add(newMethod.getSignature());
            sigBufAdd.put(original_callee_signature, sigTemp);

            /** modify all methods which invoked original method originally **/
            modifyAllCaller(newMethod, callee_signature, cg);
        }

        /** adding edge **/
        biuld_connect(caller_sMethod, newMethod);
    }


    public static void remove_nodes(SootMethod tarMethod, String src_tar_method) {
        Body tarBody = tarMethod.retrieveActiveBody();
        PatchingChain<Unit> tarUnits = tarBody.getUnits();
        //
        SootClass tarSootClass = tarMethod.getDeclaringClass();
        for (SootField sootField : tarSootClass.getFields()) {
            make_field_accessible(sootField);
        }
        make_method_accessible(tarMethod);
        String[] frameworkAPI = {"android.", "com.google", "java.", "javax.",
                "org.xml", "org.apache", "junit", "org.json",
                "org.w3c.dom"};
        for (SootClass sootClass : Scene.v().getClasses()) {
            List<SootMethod> methods = sootClass.getMethods();
            String cur_packageName = sootClass.getPackageName();
            int framework_flag = 0;
            for (int zf = 0; zf < frameworkAPI.length; zf++) {
                if (cur_packageName.startsWith(frameworkAPI[zf])) {
                    framework_flag = 1;
                    break;
                }
            }
            if (framework_flag == 1) {
                continue;
            }
            for (int z1 = 0; z1 < methods.size(); z1++) {
                SootMethod sootMethod = methods.get(z1);
                make_method_accessible(sootMethod);
                if (sootMethod.getSignature().equals("<mobi.vserv.android.adengine.VservAdManager: void onResume()>")) {
                    int az = 1;
                }
                //
                Body cur_b = null;
                try {
                    cur_b = sootMethod.retrieveActiveBody();
                } catch (Exception e) {
                    continue;
                }
                assert cur_b != null;
                Body body = cur_b;
                PatchingChain<Unit> units = cur_b.getUnits();
                HashMap<Stmt, List<Stmt>> patchMap = new HashMap<>();
                LocalGenerator lg = new LocalGenerator(body);
                int zkfFlag = 0;
                for (Unit unit : units) {
                    Stmt stmt = (Stmt) unit;
                    if (!stmt.containsInvokeExpr()) {
                        continue;
                    }
                    SootMethod sc = stmt.getInvokeExpr().getMethod();
                    if (!sc.getSignature().equals(src_tar_method)) {
                        continue;
                    }
                    // if the method invoked the method to be deleted, replace the invocation statement
                    List<Stmt> tgtStmt = new ArrayList<>();
                    tgtStmt = replace_callStmt(sootMethod, stmt, tarMethod);
                    patchMap.put(stmt, tgtStmt);
                }
                for (Stmt srcStmt : patchMap.keySet()) {
                    int zFlag = 0;
                    List<Stmt> tgtStmt = patchMap.get(srcStmt);
                    Stmt begStmt = tgtStmt.get(0);
                    for (int zi = 0; zi < tgtStmt.size(); zi++) {
                        if (!units.contains(tgtStmt.get(zi))) {
                            units.insertBefore(tgtStmt.get(zi), srcStmt);
                        }
                        if (tgtStmt.get(zi) instanceof ReturnVoidStmt) {
                            zFlag = 1;
                        }
                    }
                    if (zFlag == 1) {
                        Local lint = lg.generateLocal(IntType.v());
                        AssignStmt tarStmt = Jimple.v().newAssignStmt(lint, IntConstant.v(51));
                        units.insertAfter(tarStmt, srcStmt);

                        int zFlag2 = 0;

                        List<Object> test = Arrays.asList(units.toArray());
                        for (int zt = 0; zt < test.size(); zt++) {
                            Stmt stmt1 = (Stmt) test.get(zt);
                            if (stmt1.equals(begStmt)) {
                                zFlag2 = 1;
                            }
                            if (zFlag2 == 1) {
                                if (stmt1 instanceof ReturnVoidStmt) {
                                    GotoStmt g = Jimple.v().newGotoStmt(tarStmt);
                                    units.insertBefore(g, stmt1);
                                    units.remove(stmt1);
                                }
                            }
                            if (stmt1.equals(srcStmt)) {
                                zFlag2 = 0;
                                break;
                            }
                        }
                    }
                    units.remove(srcStmt);
                }
                sootMethod.setActiveBody(cur_b);
                cur_b.setMethod(sootMethod);
//                System.out.println(sootMethod.getSignature());
//                System.out.println(cur_b);
//                System.out.println(cur_b.getMethod().getSignature());
                cur_b.validate();
            }
        }
        // remove the method
        SootClass tarClass = tarMethod.getDeclaringClass();
        tarClass.removeMethod(tarMethod);
    }


    public static void make_method_accessible(SootMethod sMethod) {
        try {
            int zflag = sMethod.getDeclaringClass().getModifiers();
            if (Modifier.isPrivate(sMethod.getDeclaringClass().getModifiers())) {
                zflag -= Modifier.PRIVATE;
            }
            if (Modifier.isProtected(sMethod.getDeclaringClass().getModifiers())) {
                zflag -= Modifier.PROTECTED;
            }
            if (Modifier.isFinal(sMethod.getDeclaringClass().getModifiers())) {
                zflag -= Modifier.FINAL;
            }
            if (!Modifier.isPublic(sMethod.getDeclaringClass().getModifiers())) {
                zflag += Modifier.PUBLIC;
            }
//            System.out.println("zkf Modifer:\t" + Modifier.toString(zflag) + sMethod.getDeclaringClass());
            sMethod.getDeclaringClass().setModifiers(zflag);
            int mflag = sMethod.getModifiers();
            if (Modifier.isPrivate(sMethod.getModifiers())) {
                mflag -= Modifier.PRIVATE;
            }
            if (Modifier.isProtected(sMethod.getModifiers())) {
                mflag -= Modifier.PROTECTED;
            }
            if (!Modifier.isPublic(sMethod.getModifiers())) {
                mflag += Modifier.PUBLIC;
            }
//        System.out.println("zkf Modifier:\t " + Modifier.toString(mflag) + sMethod.getSignature());
            sMethod.setModifiers(mflag);
        } catch (Exception e) {
            System.out.println("zkfERROR: " + sMethod);
        }
    }


    public static SootMethod replaceMethod(String targetMethodSignature, SootClass tarClass, int count_int) {
        //
        String methodName = targetMethodSignature.split(" ")[2].split("\\(")[0];
        List<Type> paraList = new ArrayList<>();
        SootMethod targetMethod = null;
        try {
            targetMethod = Scene.v().getMethod(targetMethodSignature);
            //
            paraList = new ArrayList<>(targetMethod.getParameterTypes());
            int counttmp = count_int;
            while (counttmp > 0) {
                paraList.add(IntType.v());
                counttmp--;
            }
            Type returnType = targetMethod.getReturnType();
            int isModifier = targetMethod.getModifiers();
            SootMethod newMethod = new SootMethod(methodName,
                    paraList,
                    returnType,
                    isModifier);
            tarClass.addMethod(newMethod);
            JimpleBody jBody = Jimple.v().newBody(newMethod);
            Body tarBody = targetMethod.retrieveActiveBody();
            PatchingChain<Unit> tarUnits = tarBody.getUnits();
            jBody = (JimpleBody) tarBody.clone();
            PatchingChain units = jBody.getUnits();
            counttmp = count_int;
            Local llrTag = null;
            while (counttmp > 0) {
                LocalGenerator add_lg = new LocalGenerator(jBody);
                Local llr = add_lg.generateLocal(IntType.v());
                IdentityStmt idenStmt = Jimple.v().newIdentityStmt(llr,
                        Jimple.v().newParameterRef(IntType.v(),
                                paraList.size() - counttmp));
                counttmp--;
                units.insertBefore(idenStmt, jBody.getFirstNonIdentityStmt());
                llrTag = llr;
            }
            Stmt tar_stmt = jBody.getFirstNonIdentityStmt();
            //
            EqExpr ce = Jimple.v().newEqExpr(llrTag, IntConstant.v(1));

            Type pType = targetMethod.getReturnType();
            if (targetMethod.getReturnType() instanceof VoidType) {
                ReturnVoidStmt rtStmt = Jimple.v().newReturnVoidStmt();
                units.insertBefore(rtStmt, jBody.getFirstNonIdentityStmt());
            } else {
                ReturnStmt rtStmt;
                if (pType instanceof BooleanType
                        || pType instanceof ByteType
                        || pType instanceof CharType
                        || pType instanceof IntType
                        || pType instanceof ShortType
                ) {
                    rtStmt = Jimple.v().newReturnStmt(IntConstant.v(0));
                } else if (pType instanceof DoubleType) {
                    rtStmt = Jimple.v().newReturnStmt(DoubleConstant.v(0.0));
                } else if (pType instanceof FloatType) {
                    rtStmt = Jimple.v().newReturnStmt(DoubleConstant.v(0.0));
                } else if (pType instanceof LongType) {
                    rtStmt = Jimple.v().newReturnStmt(LongConstant.v(0));
                } else {
                    rtStmt = Jimple.v().newReturnStmt(NullConstant.v());
                }
                units.insertBefore(rtStmt, jBody.getFirstNonIdentityStmt());
            }
            // add if-invocation statement
            IfStmt stmt_1 = Jimple.v().newIfStmt(ce, tar_stmt);
            units.insertBefore(stmt_1, jBody.getFirstNonIdentityStmt());
            jBody.setMethod(newMethod);
            jBody.validate();
            newMethod.setActiveBody(jBody);
//            System.out.println("old method : \t" + targetMethod.getSignature());
            tarClass.removeMethod(targetMethod);
            check_old_method_removed(tarClass, targetMethodSignature);
//            System.out.println("newmethod body: \n" + newMethod.retrieveActiveBody());
            return newMethod;
        } catch (Exception e) {
            //
            if (e.toString().contains("already has a method with that signature")) {
//                System.err.println("e1 zkf" + methodName);
                String[] para = targetMethodSignature.split("\\(")[1].split("\\)")[0].split(",");
                List<Type> paraList1 = new ArrayList<>();
                if (!para[0].equals("")) {
                    for (int zp = 0; zp < para.length; zp++) {
                        paraList1.add(getType(para[zp]));
                    }
                }
                while (count_int > 0) {
                    paraList1.add(IntType.v());
                    count_int--;
                }
//                paraList1.add(IntType.v());
                check_old_method_removed(tarClass, targetMethodSignature);
                return tarClass.getMethod(methodName, paraList1);
            } else if (e.toString().contains("nonexistent method ")) {
                System.err.println("e2 zkf" + methodName);
                String[] para = targetMethodSignature.split("\\(")[1].split("\\)")[0].split(",");
                //
                List<Type> paraList1 = new ArrayList<>();
                if (!para[0].equals("")) {
                    for (int zp = 0; zp < para.length; zp++) {
                        paraList1.add(getType(para[zp]));
                    }
                }
                while (count_int > 0) {
                    paraList1.add(IntType.v());
                    count_int--;
                }
                check_old_method_removed(tarClass, targetMethodSignature);
                return tarClass.getMethod(methodName, paraList1);
            } else {
                System.err.println("e3 zkf:\t" + methodName);
                e.printStackTrace();
                String[] para = targetMethodSignature.split("\\(")[1].split("\\)")[0].split(",");
                //
                List<Type> paraList1 = new ArrayList<>();
                if (!para[0].equals("")) {
                    for (int zp = 0; zp < para.length; zp++) {
                        paraList1.add(getType(para[zp]));
                    }
                }
                while (count_int > 0) {
                    paraList1.add(IntType.v());
                    count_int--;
                }
//                paraList1.add(IntType.v());
                check_old_method_removed(tarClass, targetMethodSignature);
                return tarClass.getMethod(methodName, paraList1);
            }
        }
    }


    public static void rewiring(String A_signature, String B_signature, String C_signature,
                                SootClass MidType, HashMap<String, List<String>> sigBufAdd, HashMap<String, List<String>> sigBufMid,
                                ProcessManifest processManifest) {
        // parameter: the signature of three method
        // A ==> B 改为： A ==> C ==> B
        // sigBuf: <orisignature， updated && latest signature>
        String srcAsignature = A_signature;
        String srcBSignature = B_signature;
        String srcCSignature = C_signature;
        A_signature = getNewestSignature(A_signature, sigBufAdd, sigBufMid);
        B_signature = getNewestSignature(B_signature, sigBufAdd, sigBufMid);
        C_signature = getNewestSignature(C_signature, sigBufAdd, sigBufMid);
        String lstest_mid_sig;
        lstest_mid_sig = getNewestSignature(srcCSignature, sigBufAdd, sigBufMid);
        // get the return-type of method B and C
        SootMethod AMethod = Scene.v().getMethod(A_signature);
        SootMethod BMethod = Scene.v().getMethod(B_signature);
        SootMethod CMethod = Scene.v().getMethod(C_signature);
        //
        make_method_accessible(BMethod);
        make_method_accessible(CMethod);
        //
        Type BReturn = BMethod.getReturnType();
        Type CReturn = CMethod.getReturnType();
        // get the object to invoke B in method A
        SootMethod modifiedMidMethod = null;
//        SootClass MidType = createMidType(processManifest);
//        /******/
//        System.out.println("====== zkf modifing C ======");
//        System.out.println(CMethod.retrieveActiveBody());
        if ((BReturn instanceof VoidType) && (CReturn instanceof VoidType)) {
            // the return types of B and C are void
            modifiedMidMethod = modify_both_void(CMethod, BMethod);
        } else if ((BReturn instanceof VoidType) && !(CReturn instanceof VoidType)) {
            // B's return type is void, but C isn't
            modifiedMidMethod = modify_both_void(CMethod, BMethod);
        } else if (!(BReturn instanceof VoidType) && (CReturn instanceof VoidType)) {
            // C's return type is void, but B isn't
            modifiedMidMethod = modify_CVoid_BNot(CMethod, BMethod);
        } else if (!(BReturn instanceof VoidType) && (BReturn.equals(CReturn))) {
            // B C have the same return type but not void
            modifiedMidMethod = modify_same_rType(CMethod, BMethod);
        } else if (!(BReturn.equals(CReturn))) {
            // 首先都不是void， 且类型不相同
//            modifiedMidMethod = modify_mid_method(CMethod, BMethod, MidType,
//                    srcCSignature, srcBSignature, processManifest);
            modifiedMidMethod = modify_mid_method_new(CMethod, BMethod, MidType, processManifest);
        }
        // update the signature
        List<String> sigTemp = null;
        if (sigBufMid.containsKey(srcCSignature)) {
            sigTemp = sigBufMid.get(srcCSignature);
        } else {
            sigTemp = new ArrayList<>();
        }
        sigTemp.add(modifiedMidMethod.getSignature());
        sigBufMid.put(srcCSignature, sigTemp);
        MidType = updateMidType(MidType, modifiedMidMethod.getSignature(), srcCSignature, processManifest);
        make_method_accessible(AMethod);
        modify_A(AMethod, modifiedMidMethod, BMethod, C_signature, B_signature, MidType);
        modify_allCallee_in_modifyEdge(modifiedMidMethod, MidType, srcCSignature, srcBSignature, lstest_mid_sig);
    }


    public static Type getType(String typeName) {
        if (typeName.equals("int")) {
            return IntType.v();
        }
        if (typeName.equals("int[]")) {
            return IntType.v().getArrayType();
        }
        if (typeName.equals("byte")) {
            return ByteType.v();
        }
        if (typeName.equals("byte[]")) {
            return ByteType.v().getArrayType();
        }
        if (typeName.equals("char")) {
            return CharType.v();
        }
        if (typeName.equals("char[]")) {
            return CharType.v().getArrayType();
        }
        if (typeName.equals("short")) {
            return ShortType.v();
        }
        if (typeName.equals("short[]")) {
            return ShortType.v().getArrayType();
        }
        if (typeName.equals("double")) {
            return DoubleType.v();
        }
        if (typeName.equals("double[]")) {
            return DoubleType.v().getArrayType();
        }
        if (typeName.equals("float")) {
            return FloatType.v();
        }
        if (typeName.equals("float[]")) {
            return FloatType.v().getArrayType();
        }
        if (typeName.equals("long")) {
            return LongType.v();
        }
        if (typeName.equals("long[]")) {
            return LongType.v().getArrayType();
        }
        if (typeName.equals("boolean")) {
            return BooleanType.v();
        }
        if (typeName.equals("boolean[]")) {
            return BooleanType.v().getArrayType();
        }
        return RefType.v(typeName);
    }


    public static void check_old_method_removed(SootClass sootClass, String tarMethodSig) {
        try {
            SootMethod sootMethod = sootClass.getMethod(tarMethodSig);
//            System.out.println("check_old_method_removed: " + tarMethodSig + " \tnot removed  ");
            sootClass.removeMethod(sootMethod);
        } catch (Exception e) {
//            System.out.println("check_old_method_removed: " + tarMethodSig + " \tremoved  " + e);
        }
    }


    public static void modifyAllCaller(SootMethod newMethod, String callee_signature,
                                       HashMap<String, HashMap<String, HashSet<String>>> cg) {
        String[] frameworkAPI = {"android.", "com.google", "java.", "javax.",
                "org.xml", "org.apache", "junit", "org.json",
                "org.w3c.dom"};
        for (SootClass sClass : Scene.v().getApplicationClasses()) {
            /** 若是framework api 直接跳过 **/
            String cur_packageName = sClass.getPackageName();
            int framework_flag = 0;
            for (int zf = 0; zf < frameworkAPI.length; zf++) {
                if (cur_packageName.startsWith(frameworkAPI[zf])) {
                    framework_flag = 1;
                    break;
                }
            }
            if (framework_flag == 1) {
                continue;
            }
            List<SootMethod> methods = sClass.getMethods();
            /** deal with methods **/
            for (int z1 = 0; z1 < methods.size(); z1++) {
                SootMethod sootMethod = methods.get(z1);
                Body cur_b = null;
                try {
                    cur_b = sootMethod.retrieveActiveBody();
                } catch (Exception e) {
                    continue;
                }
                assert cur_b != null;
                Body jBody = cur_b;
                PatchingChain<Unit> cUnits = cur_b.getUnits();
                HashMap<Stmt, Stmt> patchMap = new HashMap();
                LocalGenerator lg = new LocalGenerator(jBody);
                for (Unit unit : cUnits) {
                    Stmt stmt = (Stmt) unit;
                    if (!stmt.containsInvokeExpr()) {   // 找到invoke
                        continue;
                    }
                    boolean flag = false;
                    SootMethod tar_Method = stmt.getInvokeExpr().getMethod();

                    if (tar_Method.getSignature().equals(callee_signature)) {
                        flag = true;
                    }
                    if (flag == false) { //
                        String real_name = sootMethod.getSignature();
//                    System.out.println("zkf+cur method sig: "+real_name);
                        if (!cg.containsKey(real_name)) {
                            real_name = real_name.replace(",int)", ")");
//                        System.out.println("\tzkf+cur method sig: "+real_name);
                            if (!cg.containsKey(real_name)) {
                                real_name = real_name.replace("(int)", "()");
//                            System.out.println("\t\tzkf+cur method sig: "+real_name);
                                if (!cg.containsKey(real_name)) {
                                    continue;
                                }
                            }
                        }
                        if (!cg.get(real_name).containsKey(unit.toString())) {
                            continue;
                        }
                        HashSet<String> tmp = cg.get(real_name).get(unit.toString());

                        flag = tmp.contains(callee_signature);
                    }
                    if (flag) {
//                        System.out.println("~~~~~~ zzzz modifying invoke method ~~~~~");
//                        System.out.println("\t " + sootMethod.getSignature() + " ==> " + callee_signature);
                        int paraLeng = stmt.getInvokeExpr().getUseBoxes().size();
                        ArrayList<Value> cur_parameterList = new ArrayList<>();
                        int ori_para_count = stmt.getInvokeExpr().getArgCount();
                        for (int zpl = 0; zpl < ori_para_count; zpl++) {
                            cur_parameterList.add(stmt.getInvokeExpr().getArg(zpl));
                        }
                        for (int zpl = ori_para_count; zpl < newMethod.getParameterCount(); zpl++) {
                            cur_parameterList.add(IntConstant.v(1));
                        }
                        List<Type> old_para = new ArrayList<>(stmt.getInvokeExpr().getMethod().getParameterTypes());
                        for (int zpl = ori_para_count; zpl < newMethod.getParameterCount(); zpl++) {
                            old_para.add(IntType.v());
                        }
//                        old_para.add(IntType.v());
                        SootMethodRef smr = Scene.v().makeMethodRef(tar_Method.getDeclaringClass(),
                                newMethod.getName(),
                                old_para,
                                newMethod.getReturnType(),
                                newMethod.isStatic()
                        );
//                        System.out.println("new method ref: \t" + smr);
                        String cur_invokeType = stmt.getInvokeExpr().toString().split(" ")[0];
                        InvokeExpr cur_invokeExpr = null;
                        Stmt newStmt = null;
                        if (paraLeng == 0) {
//                            System.out.println("paraLeng == 0 ");
                            cur_invokeExpr = Jimple.v().newStaticInvokeExpr(smr, cur_parameterList);
                            if (stmt instanceof AssignStmt) {
                                Local lo = (Local) ((AssignStmt) stmt).getLeftOp();
                                newStmt = Jimple.v().newAssignStmt(lo, cur_invokeExpr);
                            } else {
                                newStmt = Jimple.v().newInvokeStmt(cur_invokeExpr);
                            }
                            patchMap.put(stmt, newStmt);
                        } else {
//                            System.out.println("paraLeng != 0 ");
                            if (cur_invokeType.equals("staticinvoke")) {
                                cur_invokeExpr = Jimple.v().newStaticInvokeExpr(smr, cur_parameterList);
                            } else {
                                Local cur_local = (Local) stmt.getInvokeExpr().getUseBoxes().get(paraLeng - 1).getValue();
                                if (cur_invokeType.equals("specialinvoke")) {
                                    cur_invokeExpr = Jimple.v().newSpecialInvokeExpr(cur_local, smr, cur_parameterList);
                                } else if (cur_invokeType.equals("virtualinvoke")) {
                                    cur_invokeExpr = Jimple.v().newVirtualInvokeExpr(cur_local, smr, cur_parameterList);
                                } else if (cur_invokeType.equals("interfaceinvoke")) {
                                    cur_invokeExpr = Jimple.v().newInterfaceInvokeExpr(cur_local, smr, cur_parameterList);
                                } else if (cur_invokeType.equals("staticinvoke")) {
                                    cur_invokeExpr = Jimple.v().newStaticInvokeExpr(smr, cur_parameterList);
                                } else {
                                    cur_invokeExpr = Jimple.v().newVirtualInvokeExpr(cur_local, smr, cur_parameterList);
                                }
                            }
                            if (stmt instanceof AssignStmt) {
                                Local lo = (Local) ((AssignStmt) stmt).getLeftOp();
                                newStmt = Jimple.v().newAssignStmt(lo, cur_invokeExpr);
                            } else {
                                newStmt = Jimple.v().newInvokeStmt(cur_invokeExpr);
                            }
                            patchMap.put(stmt, newStmt);
                        }
//                        System.out.println("~~~~~~  invoke method modified ~~~~~");
//                        System.out.println("被修改了： " + tar_Method.getSignature());
                    }
                }
                for (Stmt srcStmt : patchMap.keySet()) {
                    Stmt tgtSmtmt = patchMap.get(srcStmt);
//                    System.out.println("modified path: [zzz] " + srcStmt + " --> " + tgtSmtmt);
                    cUnits.insertAfter(tgtSmtmt, srcStmt);
                    cUnits.remove(srcStmt);
                }
                cur_b.validate();
            }
        }
    }


    public static Value setDefaultValue(Type pType, Body body) {
        if (pType instanceof BooleanType
                || pType instanceof ByteType
                || pType instanceof CharType
                || pType instanceof IntType
                || pType instanceof ShortType
        ) {
            return IntConstant.v(0);
        } else if (pType instanceof DoubleType) {
            return DoubleConstant.v(0.0);
        } else if (pType instanceof FloatType) {
            return DoubleConstant.v(0.0);
        } else if (pType instanceof LongType) {
            return LongConstant.v(0);
        } else {
            return NullConstant.v();
        }
    }


    public static void biuld_connect(SootMethod caller_method, SootMethod callee_method) {
        Body caller_body = caller_method.retrieveActiveBody();
        SootClass caller_class = caller_method.getDeclaringClass();
        SootClass callee_class = callee_method.getDeclaringClass();
        PatchingChain units = caller_body.getUnits();
        ArrayList<Value> parameterList = new ArrayList<>();
        for (int zpl = 0; zpl < callee_method.getParameterCount() - 1; zpl++) {
            /** POINT **/
            parameterList.add(setDefaultValue(callee_method.getParameterType(zpl), caller_body));
        }
        parameterList.add(IntConstant.v(0));
        //
        List<Unit> generatedUnits = new ArrayList<>();
        //
        LocalGenerator caller_lg = new LocalGenerator(caller_body);
        if (callee_method.isStatic()) {
            Local llc = caller_lg.generateLocal(callee_class.getType());
            InvokeExpr invokeExpr = Jimple.v().newStaticInvokeExpr(
                    callee_method.makeRef(),
                    parameterList);
            Stmt stmt_1;
            if (callee_method.getReturnType() instanceof VoidType) {
                stmt_1 = Jimple.v().newInvokeStmt(invokeExpr);
            } else {
                Local return_l = caller_lg.generateLocal(callee_method.getReturnType());
                stmt_1 = Jimple.v().newAssignStmt(return_l, invokeExpr);
            }
            generatedUnits.add(stmt_1);
        } else {
            String filedName = "";
            if (!callee_class.getName().equals(caller_class.getName()) || (caller_method.isStatic() && !callee_method.isStatic())) {
                // in different class
                Local callee_object = caller_lg.generateLocal(callee_class.getType());
                NewExpr caObj = Jimple.v().newNewExpr(RefType.v(callee_class));
                AssignStmt aStmt = Jimple.v().newAssignStmt(callee_object, caObj);
                generatedUnits.add(aStmt);
                SootMethod ctm = null;
                for (SootMethod sm : callee_class.getMethods()) {
                    if (sm.getName().contains("<init>")) {
                        if (sm.getParameterCount() == 0) {
                            ctm = sm;
                            break;
                        }
                    }
                }
                if (ctm == null) {
                    for (SootMethod sm : callee_class.getMethods()) {
                        if (sm.getName().contains("<clinit>")) {
                            if (sm.getParameterCount() == 0) {
                                ctm = sm;
                                break;
                            }
                        }
                    }
                }
                if (ctm == null) {
                    for (SootMethod sm : callee_class.getMethods()) {
                        if (sm.getName().contains("<init>")) {
                            ctm = sm;
                            break;
                        }
                    }
                }
                make_method_accessible(ctm);
                ArrayList<Value> init_object_pl = new ArrayList<>();
                if (ctm.getParameterCount() > 0) {
                    for (int zip = 0; zip < ctm.getParameterCount(); zip++) {
                        init_object_pl.add(setDefaultValue(ctm.getParameterType(zip), caller_body));
                    }
                }
                InvokeExpr ie = null;
                if (ctm.isStatic()) {
                    ie = Jimple.v().newStaticInvokeExpr(
                            ctm.makeRef(),
                            init_object_pl);
                } else {
                    ie = Jimple.v().newSpecialInvokeExpr(callee_object,
                            ctm.makeRef(),
                            init_object_pl);
                }
                Stmt t1 = Jimple.v().newInvokeStmt(ie);
                generatedUnits.add(t1);
                //
                InvokeExpr invokeExpr = Jimple.v().newVirtualInvokeExpr(callee_object,
                        callee_method.makeRef(),
                        parameterList);
                Stmt stmt_1;
                if (callee_method.getReturnType() instanceof VoidType) {
                    stmt_1 = Jimple.v().newInvokeStmt(invokeExpr);
                } else {
                    Local return_l = caller_lg.generateLocal(callee_method.getReturnType());
                    stmt_1 = Jimple.v().newAssignStmt(return_l, invokeExpr);
                }
                generatedUnits.add(stmt_1);
            } else {
                // caller callee in the same class
                if (Modifier.isStatic(caller_method.getModifiers())) {
                    // do nothing
                }
                Local same_class = caller_body.getThisLocal();
                InvokeExpr invokeExpr = Jimple.v().newVirtualInvokeExpr(same_class,
                        callee_method.makeRef(),
                        parameterList);
                Stmt stmt_1;
                if (callee_method.getReturnType() instanceof VoidType) {
                    stmt_1 = Jimple.v().newInvokeStmt(invokeExpr);
                } else {
                    Local return_l = caller_lg.generateLocal(callee_method.getReturnType());
                    stmt_1 = Jimple.v().newAssignStmt(return_l, invokeExpr);
                }
                generatedUnits.add(stmt_1);
            }
        }
        units.insertBefore(generatedUnits, units.getLast());
        caller_body.validate();
        caller_method.setActiveBody(caller_body);
    }


    public static SootMethod modify_both_void(SootMethod mid_method,
                                              SootMethod tar_method) {
        String methodName = mid_method.getName();
        List<Type> paraList = new ArrayList<>();
        paraList.addAll(mid_method.getParameterTypes());
        List<Type> tarParaList = new ArrayList<>();
        tarParaList.addAll(tar_method.getParameterTypes());
        paraList.addAll(tarParaList);
        paraList.add(tar_method.getDeclaringClass().getType()); // the object to invoke B 调用B所需要的对象
        paraList.add(IntType.v());  // flag
        // Create new method
        SootMethod newMidMethod = new SootMethod(methodName,
                paraList,
                mid_method.getReturnType(),
                mid_method.getModifiers());
        SootClass midClass = mid_method.getDeclaringClass();
        midClass.addMethod(newMidMethod);
        Body midBody = mid_method.retrieveActiveBody();
        Body newMidBody = Jimple.v().newBody();
        newMidBody = (Body) midBody.clone();
        PatchingChain units = newMidBody.getUnits();
        LocalGenerator lg = new LocalGenerator(newMidBody);
        JimpleBody jNewMidBody = (JimpleBody) newMidBody;
        // get the target of if-statement 先获取if语句的 goto target
        Unit ifTar = jNewMidBody.getFirstNonIdentityStmt();
        // Step 1: insert 'identity statement' of new parameters  插入新paramter的identity statement
        int idx = mid_method.getParameterCount();
        int tarParaNum = tar_method.getParameterCount();
        Local[] llr = new Local[tarParaNum + 2];
        for (int zp = 0; zp < tarParaNum + 2; zp++) { // 加上call B.obj, 和flag
            llr[zp] = lg.generateLocal(paraList.get(idx + zp));
            IdentityStmt identityStmt = Jimple.v().newIdentityStmt(llr[zp],
                    Jimple.v().newParameterRef(paraList.get(idx + zp),
                            zp + idx));
            units.insertBefore(identityStmt, jNewMidBody.getFirstNonIdentityStmt());
        }
        // set condition statement of if 设置if 条件语句
        EqExpr ifEq = Jimple.v().newEqExpr(llr[tarParaNum + 1], IntConstant.v(1));// if true, work normally 如果为1，正常执行
        // set the if-bocy 设置if 语句体，主要是调用 B，并return
        int tarModifier = tar_method.getModifiers();
        InvokeExpr invokeExpr = null;
        List<Value> BPara = new ArrayList<>();
        for (int zp = 0; zp < tarParaNum; zp++) {
            BPara.add(llr[zp]);
        }
        // 对B是否是statci判断
        if (Modifier.isStatic(tar_method.getModifiers())) {
            invokeExpr = Jimple.v().newStaticInvokeExpr(tar_method.makeRef(), BPara);
        } else {
            make_method_accessible(tar_method);
            invokeExpr = Jimple.v().newVirtualInvokeExpr(llr[tarParaNum],
                    tar_method.makeRef(),
                    BPara);
        }
        Stmt invokeBStmt = Jimple.v().newInvokeStmt(invokeExpr);
        Type midReturnType = mid_method.getReturnType();
        ReturnStmt rStmt = null;
        if (midReturnType instanceof VoidType) {
            ReturnVoidStmt rStmt1 = Jimple.v().newReturnVoidStmt();
            units.insertBefore(rStmt1, jNewMidBody.getFirstNonIdentityStmt());
        } else {
            rStmt = Jimple.v().newReturnStmt(setDefaultValue(midReturnType, midBody));
            units.insertBefore(rStmt, jNewMidBody.getFirstNonIdentityStmt());
        }
//        units.insertBefore(rStmt, jNewMidBody.getFirstNonIdentityStmt());
        units.insertBefore(invokeBStmt, jNewMidBody.getFirstNonIdentityStmt());
        // if 语句
        IfStmt ifStmt = Jimple.v().newIfStmt(ifEq, ifTar);
        units.insertBefore(ifStmt, jNewMidBody.getFirstNonIdentityStmt());
        jNewMidBody.setMethod(newMidMethod);
        jNewMidBody.validate();
        newMidMethod.setActiveBody(newMidBody);
        midClass.removeMethod(mid_method);
        return newMidMethod;
    }


    public static SootMethod modify_CVoid_BNot(SootMethod mid_method,
                                               SootMethod tar_method) {
        String methodName = mid_method.getName();
        List<Type> paraList = new ArrayList<>();
        paraList.addAll(mid_method.getParameterTypes());
        List<Type> tarParaList = new ArrayList<>();
        tarParaList.addAll(tar_method.getParameterTypes());
        paraList.addAll(tarParaList);
        paraList.add(tar_method.getDeclaringClass().getType());
        paraList.add(IntType.v());
        // 构建方法
        SootMethod newMidMethod = new SootMethod(methodName,
                paraList,
                tar_method.getReturnType(),
                mid_method.getModifiers());
        SootClass midClass = mid_method.getDeclaringClass();
        midClass.addMethod(newMidMethod);
        Body midBody = mid_method.retrieveActiveBody();
        Body newMidBody = Jimple.v().newBody(newMidMethod);
        newMidBody = (Body) midBody.clone();
        JimpleBody jNewMidBody = (JimpleBody) newMidBody;
        PatchingChain<Unit> units = newMidBody.getUnits();
        LocalGenerator lg = new LocalGenerator(newMidBody);
        // 修改所有返回语句, 返回为b类型的默认值
        HashMap<Stmt, Stmt> patchMap = new HashMap();
        for (Unit unit : units) {
            Stmt stmt = (Stmt) unit;
            if (stmt instanceof ReturnStmt || stmt instanceof ReturnVoidStmt) {
                ReturnStmt newStmt = Jimple.v().newReturnStmt(
                        setDefaultValue(tar_method.getReturnType(), newMidBody));
                patchMap.put(stmt, newStmt);
            }
        }
        for (Stmt srcStmt : patchMap.keySet()) {
            Stmt tgtStmt = patchMap.get(srcStmt);
            units.insertAfter(tgtStmt, srcStmt);
            units.remove(srcStmt);
        }
        // 获取 if 的 goto tar units
        Unit ifTar = jNewMidBody.getFirstNonIdentityStmt();
        // 开始修改
        // Step 1:  插入新的parameters 的 identity statement
        int idx = mid_method.getParameterCount();
        int tarParaNum = tar_method.getParameterCount();
        Local[] llr = new Local[tarParaNum + 2];
        for (int zp = 0; zp < tarParaNum + 2; zp++) {
            llr[zp] = lg.generateLocal(paraList.get(idx + zp));
            IdentityStmt identityStmt = Jimple.v().newIdentityStmt(llr[zp],
                    Jimple.v().newParameterRef(paraList.get(idx + zp),
                            zp + idx));
            units.insertBefore(identityStmt, jNewMidBody.getFirstNonIdentityStmt());
        }
        // 设置if eq语句
        EqExpr ifEq = Jimple.v().newEqExpr(llr[tarParaNum + 1], IntConstant.v(1));
        // 设置if 语句体， 主要是调用B， 并return TypeB_returnType
        // 获取B的参数
        List<Value> BPara = new ArrayList<>();
        for (int zp = 0; zp < tarParaNum; zp++) {
            BPara.add(llr[zp]);
        }
        // 对B是否是static判断
        InvokeExpr invokeExpr = null;
        if (Modifier.isStatic(tar_method.getModifiers())) {
            invokeExpr = Jimple.v().newStaticInvokeExpr(tar_method.makeRef(), BPara);
        } else {
            make_method_accessible(tar_method);
            invokeExpr = Jimple.v().newVirtualInvokeExpr(llr[tarParaNum],
                    tar_method.makeRef(), BPara);
        }
        // 建立b的返回类型的local
        Local bReturn = lg.generateLocal(tar_method.getReturnType());
        AssignStmt aStmt = Jimple.v().newAssignStmt(bReturn, invokeExpr);
        ReturnStmt rStmt = Jimple.v().newReturnStmt(bReturn);
        units.insertBefore(rStmt, jNewMidBody.getFirstNonIdentityStmt());
        units.insertBefore(aStmt, jNewMidBody.getFirstNonIdentityStmt());
        IfStmt ifStmt = Jimple.v().newIfStmt(ifEq, ifTar);
        units.insertBefore(ifStmt, jNewMidBody.getFirstNonIdentityStmt());
        jNewMidBody.setMethod(newMidMethod);
        jNewMidBody.validate();
        newMidMethod.setActiveBody(newMidBody);
        midClass.removeMethod(mid_method);
        return newMidMethod;
    }


    public static SootMethod modify_same_rType(SootMethod mid_method,
                                               SootMethod tar_method) {
//        System.out.println("====== zkf modified C  modify_same_rType======");

        // 或 B C都不是return void，但 B C 返回类型相同
        // 产生的结果： 调用B和调用C时，调用语句保存的返回值都不需要修改
        String methodName = mid_method.getName();
        List<Type> paraList = new ArrayList<>();
        paraList.addAll(mid_method.getParameterTypes());
        List<Type> tarParaList = new ArrayList<>();
        tarParaList.addAll(tar_method.getParameterTypes());
        paraList.addAll(tarParaList);
        paraList.add(tar_method.getDeclaringClass().getType()); // 调用B所需要的对象
        paraList.add(IntType.v());  // flag

        // 构建新方法
        SootMethod newMidMethod = new SootMethod(methodName,
                paraList,
                mid_method.getReturnType(),
                mid_method.getModifiers());
        SootClass midClass = mid_method.getDeclaringClass();
        midClass.addMethod(newMidMethod);
        Body midBody = mid_method.retrieveActiveBody();
        Body newMidBody = (Body) midBody.clone();
//        newMidBody = (Body) midBody.clone();
        PatchingChain units = newMidBody.getUnits();
        LocalGenerator lg = new LocalGenerator(newMidBody);
        JimpleBody jNewMidBody = (JimpleBody) newMidBody;
        // 先获取if语句的 goto target
        Unit ifTar = jNewMidBody.getFirstNonIdentityStmt();
        // 开始
        // Step 1:  插入新paramter的identity statement
        int idx = mid_method.getParameterCount();
        int tarParaNum = tar_method.getParameterCount();
        Local[] llr = new Local[tarParaNum + 2];
        for (int zp = 0; zp < tarParaNum + 2; zp++) { // 加上call B.obj, 和flag
            llr[zp] = lg.generateLocal(paraList.get(idx + zp));
            IdentityStmt identityStmt = Jimple.v().newIdentityStmt(llr[zp],
                    Jimple.v().newParameterRef(paraList.get(idx + zp),
                            zp + idx));
            units.insertBefore(identityStmt, jNewMidBody.getFirstNonIdentityStmt());
        }
        // 设置if 条件语句
        EqExpr ifEq = Jimple.v().newEqExpr(llr[tarParaNum + 1], IntConstant.v(1));// 如果为1，正常执行
        // 设置if 语句体，主要是调用 B，并return
        int tarModifier = tar_method.getModifiers();
        InvokeExpr invokeExpr = null;
        List<Value> BPara = new ArrayList<>();
        for (int zp = 0; zp < tarParaNum; zp++) {
            BPara.add(llr[zp]);
        }
        // static
        if (Modifier.isStatic(tar_method.getModifiers())) {
            invokeExpr = Jimple.v().newStaticInvokeExpr(tar_method.makeRef(), BPara);
        } else {
            make_method_accessible(tar_method);
            invokeExpr = Jimple.v().newVirtualInvokeExpr(llr[tarParaNum],
                    tar_method.makeRef(),
                    BPara);
        }
        Local returnPara = lg.generateLocal(mid_method.getReturnType());
        Stmt invokeBStmt = null;
        if (mid_method.getReturnType() instanceof VoidType) {
            invokeBStmt = Jimple.v().newInvokeStmt(invokeExpr);
        } else {
            invokeBStmt = Jimple.v().newAssignStmt(returnPara, invokeExpr);
        }
//        Stmt invokeBStmt = Jimple.v().newInvokeStmt(invokeExpr);
        Type midReturnType = mid_method.getReturnType();
        ReturnStmt rStmt = null;
        if (midReturnType instanceof VoidType) {
            rStmt = (ReturnStmt) Jimple.v().newReturnVoidStmt();
        } else {
            rStmt = Jimple.v().newReturnStmt(returnPara);
        }
        units.insertBefore(rStmt, jNewMidBody.getFirstNonIdentityStmt());
        units.insertBefore(invokeBStmt, jNewMidBody.getFirstNonIdentityStmt());
        // if 语句
        IfStmt ifStmt = Jimple.v().newIfStmt(ifEq, ifTar);
        units.insertBefore(ifStmt, jNewMidBody.getFirstNonIdentityStmt());
        jNewMidBody.setMethod(newMidMethod);
        jNewMidBody.validate();
        newMidMethod.setActiveBody(newMidBody);
        midClass.removeMethod(mid_method);
        return newMidMethod;
    }


    public static SootMethod modify_mid_method_new(SootMethod mid_method,
                                                   SootMethod tar_method,
                                                   SootClass MidType,
                                                   ProcessManifest processManifest) {
//        System.out.println("====== zkf modified C modify_mid_method_new ======");
        // mid_method: 中间的方法 C
        // tar_method: 最终需要调用的方法 B
        // typeMid: 保存了C 和 B的返回类型的结构体
        /** B 和 C的返回类型都不为空，且不相同 **/
        //Step 1: 添加参数，加入methodB的参数，加入int
        //          修改返回类型，为typeMid
        String methodName = mid_method.getName();
        List<Type> paraList = new ArrayList<>();
        paraList.addAll(mid_method.getParameterTypes());
        List<Type> tarParaList = new ArrayList<>();
        tarParaList.addAll(tar_method.getParameterTypes());
        paraList.addAll(tarParaList);
//        for (int zi = 0; zi < tarParaList.size(); zi++) {
//            paraList.add(tarParaList.get(zi));
//        }
        paraList.add(tar_method.getDeclaringClass().getType());
        paraList.add(IntType.v());
        MidType = updateMidType(MidType, mid_method.getSignature(), tar_method.getSignature(), processManifest);
        SootMethod newMidMethod = new SootMethod(methodName,
                paraList,
                MidType.getType(),
                mid_method.getModifiers());
        SootClass midClass = mid_method.getDeclaringClass();
        midClass.addMethod(newMidMethod);
        Body midBody = mid_method.retrieveActiveBody();
        Body newMidBody = Jimple.v().newBody();
        //
        newMidBody = (Body) midBody.clone();
        PatchingChain<Unit> units = newMidBody.getUnits();
        LocalGenerator lg = new LocalGenerator(newMidBody);
        //
        JimpleBody jNewMidBody = (JimpleBody) newMidBody;
        Unit if_tar = jNewMidBody.getFirstNonIdentityStmt();
        List<Unit> generatedUnits = new ArrayList<>();
        // 插入新parameter的identity statement
        int idx = mid_method.getParameterCount();
        int add_para_num = tar_method.getParameterCount();
        Local[] llr = new Local[add_para_num + 2];
        for (int zp = 0; zp < add_para_num + 2; zp++) {
            llr[zp] = lg.generateLocal(paraList.get(zp + idx));
            IdentityStmt identityStmt = Jimple.v().newIdentityStmt(llr[zp],
                    Jimple.v().newParameterRef(paraList.get(zp + idx),
                            zp + idx));
            units.insertBefore(identityStmt, jNewMidBody.getFirstNonIdentityStmt());
        }
        // 获取所有return语句，更换为新的return 语句
        // step1: 先新建新返回类型的对象
        Local globalNewReturnType = lg.generateLocal(MidType.getType());
        // Step 2: 遍历body，修改所有return语句
        HashMap<Stmt, List<Stmt>> patchMap = new HashMap<>();
        for (Unit unit : units) {
            Stmt stmt = (Stmt) unit;
            if (stmt instanceof ReturnStmt) {
                List<Stmt> tmp = new ArrayList<>();
                Value r = stmt.getUseBoxes().get(0).getValue();
                //  如果返回类型和方法的返回类型相同，则不用修改
                // 对应情况：该方法已经被修改过，
//                if (r.getType().toString().equals(newMidMethod.getReturnType().toString())) {
//                    continue;
//                }
                // 将r保存到MidType的 B 的返回类型中
                NewExpr creat_Midtype = Jimple.v().newNewExpr(MidType.getType());
                AssignStmt aStmt_in = Jimple.v().newAssignStmt(globalNewReturnType, creat_Midtype);
                tmp.add(aStmt_in);
                SootMethod midTypeInit = MidType.getMethodByName("<init>");
                InvokeExpr invokeExpr = Jimple.v().newSpecialInvokeExpr(globalNewReturnType, midTypeInit.makeRef());
                InvokeStmt invokeStmt = Jimple.v().newInvokeStmt(invokeExpr);
                tmp.add(invokeStmt);
                //
                InstanceFieldRef ifr = Jimple.v().newInstanceFieldRef(globalNewReturnType,
                        MidType.getFieldByName(getFieldNameZ(mid_method.getSignature())).makeRef());
                AssignStmt aStmt_4 = Jimple.v().newAssignStmt(ifr, r);
                tmp.add(aStmt_4);
                //
                ReturnStmt returnStmt = Jimple.v().newReturnStmt(globalNewReturnType);
                tmp.add(returnStmt);
                patchMap.put(stmt, tmp);
            }
        }
        for (Stmt srcStmt : patchMap.keySet()) {
            List<Stmt> tgtStmt = patchMap.get(srcStmt);
            for (int zi = 0; zi < tgtStmt.size(); zi++) {
                units.insertBefore(tgtStmt.get(zi), srcStmt);
            }
            if (srcStmt.equals(if_tar)) {
                if_tar = tgtStmt.get(0);
            }
            units.remove(srcStmt);
        }
        // 在body 头插入if语句，判断当前是调用B还是C
        // 初始化新的类型的对象
        Local newReturnType = lg.generateLocal(MidType.getType());
        NewExpr create_obj = Jimple.v().newNewExpr(MidType.getType());
        AssignStmt aStmt_1 = Jimple.v().newAssignStmt(newReturnType, create_obj);
        generatedUnits.add(aStmt_1);
        //
        SootMethod objInit = MidType.getMethodByName("<init>");
        InvokeExpr ie = Jimple.v().newSpecialInvokeExpr(newReturnType, objInit.makeRef());
        InvokeStmt iStmt_1 = Jimple.v().newInvokeStmt(ie);
        generatedUnits.add(iStmt_1);
        // 添加if 条件语句
        EqExpr ifEq = Jimple.v().newEqExpr(llr[add_para_num + 1], IntConstant.v(1)); // if flag == 1,正常执行
        // 添加if 体
        // 调用B
//        Local returnB = lg.generateLocal(tar_method.getReturnType());// 此处应用srcSig中获取调用类型，因为B可能被修改过
        //
        Type srcReturnB = tar_method.getReturnType();
        Local returnB = lg.generateLocal(srcReturnB);
        //
        ArrayList<Value> para_B = new ArrayList<>();
        for (int zp = 0; zp < tar_method.getParameterCount(); zp++) {
            para_B.add(llr[zp]);
        }
        // 对B是否是static 判断
        InvokeExpr callB = null;
        if (Modifier.isStatic(tar_method.getModifiers())) {
            callB = Jimple.v().newStaticInvokeExpr(tar_method.makeRef(), para_B);
        } else {
            make_method_accessible(tar_method);
            callB = Jimple.v().newVirtualInvokeExpr(llr[tar_method.getParameterCount()],
                    tar_method.makeRef(), para_B);
        }
        // 保存B的返回值
        AssignStmt aStmt_2 = Jimple.v().newAssignStmt(returnB, callB);
        generatedUnits.add(aStmt_2);
        // 将B的返回值存到新返回类型中
//        InstanceFieldRef instanceFieldRef = Jimple.v().newInstanceFieldRef(newReturnType,
//                MidType.getFieldByName(getFieldNameZ(tar_method)).makeRef());
        InstanceFieldRef instanceFieldRef = Jimple.v().newInstanceFieldRef(newReturnType,
                MidType.getFieldByName(getFieldNameZ(tar_method.getSignature())).makeRef());
        AssignStmt aStmt_3 = Jimple.v().newAssignStmt(instanceFieldRef, returnB);
        generatedUnits.add(aStmt_3);
        //return 新返回类型
        ReturnStmt returnStmt_0 = Jimple.v().newReturnStmt(newReturnType);
        generatedUnits.add(returnStmt_0);
        // 插入 if 体到body 中
        units.insertBefore(generatedUnits, jNewMidBody.getFirstNonIdentityStmt());
        // 插入 if 语句
        IfStmt ifStmt = Jimple.v().newIfStmt(ifEq, if_tar);
//        units.insertBefore(generatedUnits, jNewMidBody.getFirstNonIdentityStmt());
        units.insertBefore(ifStmt, jNewMidBody.getFirstNonIdentityStmt());
        jNewMidBody.setMethod(newMidMethod);
        jNewMidBody.validate();
        newMidMethod.setActiveBody(newMidBody);
        make_method_accessible(newMidMethod);
        midClass.removeMethod(mid_method);
        return newMidMethod;
    }


    public static String getFieldNameZ(String methodSignature) {
        methodSignature = methodSignature.substring(1, methodSignature.length() - 1);
        String[] element = methodSignature.split(" ");
        String name = element[0].split(":")[0].replace(".", "_") + "_"
                + getReturnTypeZ(element[1]) + "_" +
                element[element.length - 1].split("\\(")[0].replace(".", "_");
        return name;
    }


    public static String getReturnTypeZ(String typeName) {
        if (typeName.contains("[]")) {
            typeName.replace("[]", "Array");
        }
        typeName = typeName.replace(".", "_");
        return typeName;
    }


    public static SootClass updateMidType(SootClass MidType, String method1, String method2,
                                          ProcessManifest processManifest) {
        // update MidType class
        String f1_name = getFieldNameZ(method1);
//        SootField f1 = Scene.v().makeSootField(f1_name, method1.getReturnType());
        SootField f1 = Scene.v().makeSootField(f1_name, getType(method1.split(" ")[1]), Modifier.PUBLIC);

        int flag = 0;
        for (SootField sootField : MidType.getFields()) {
            if (sootField.getName().equals(f1_name)) {
                flag = 1;
            }
        }
        if (flag == 0) {
            MidType.addField(f1);
        }
        String f2_name = getFieldNameZ(method2);
        SootField f2 = Scene.v().makeSootField(f2_name, getType(method2.split(" ")[1]), Modifier.PUBLIC);
        flag = 0;
        for (SootField sootField : MidType.getFields()) {
            if (sootField.getName().equals(f2_name)) {
                flag = 1;
            }
        }
        if (flag == 0) {
            MidType.addField(f2);
        }
        //如果初始化方法存在，先删除
        if (MidType.getMethodCount() > 0) {
            SootMethod sm = MidType.getMethodByName("<init>");
            MidType.removeMethod(sm);
        }
        //
        SootMethod initMethod = new SootMethod("<init>",
                null,
                VoidType.v(), Modifier.PUBLIC);
        MidType.addMethod(initMethod);
        Body body = Jimple.v().newBody(initMethod);
        JimpleBody jimpleBody = (JimpleBody) body;
        PatchingChain units = body.getUnits();
        LocalGenerator lg = new LocalGenerator(body);
        Local thisPara = lg.generateLocal(MidType.getType());
        IdentityStmt identityStmt = Jimple.v().newIdentityStmt(thisPara,
                Jimple.v().newThisRef(MidType.getType()));
        units.add(identityStmt);
        SootMethod objInit = Scene.v().getMethod("<java.lang.Object: void <init>()>");
        SpecialInvokeExpr specialInvokeExpr = Jimple.v().newSpecialInvokeExpr(thisPara,
                objInit.makeRef());
        Stmt initMidType = Jimple.v().newInvokeStmt(specialInvokeExpr);
        units.add(initMidType);
        //
        for (SootField sootField : MidType.getFields()) {
            Type type = sootField.getType();
//            field_lo[count] = lg.generateLocal(type);
            InstanceFieldRef ifr = Jimple.v().newInstanceFieldRef(thisPara,
                    sootField.makeRef());
//            AssignStmt assignStmt = Jimple.v().newAssignStmt(field_lo[count], setDefaultValue(type,body));
            AssignStmt assignStmt = Jimple.v().newAssignStmt(ifr, setDefaultValue(type, body));

//            units.insertBefore(assignStmt, jimpleBody.getFirstNonIdentityStmt());
            units.add(assignStmt);
//            count++;
        }
        Stmt returnStmt = Jimple.v().newReturnVoidStmt();
        units.add(returnStmt);
        body.setMethod(initMethod);
        initMethod.setActiveBody(body);
        body.validate();
        return MidType;
    }


    public static void modify_A(SootMethod src_method, SootMethod mid_method,
                                SootMethod tar_method, String src_mid_sig,
                                String src_tar_sig, SootClass MidType) {
        Body body = src_method.retrieveActiveBody();
        PatchingChain<Unit> units = body.getUnits();
        LocalGenerator lg = new LocalGenerator(body);
//        Type BReturnType = tar_method.getReturnType();
//        Type CReturnType = mid_method.getReturnType();
        HashMap<Stmt, List<Stmt>> patchMap = new HashMap<>();
        // 遍历方法体，找到 srcMethod 中所有调用 tarMethod 的语句，并进行相应的替换
        // find all statements that invoke srcMehtod, and modify them accordingly
        for (Unit unit : units) {
            Stmt stmt = (Stmt) unit;
            if (!stmt.containsInvokeExpr()) {
                continue;
            }
            List<Stmt> tgtStmt = new ArrayList<>();
            SootMethod sootMethod = stmt.getInvokeExpr().getMethod();
            if (sootMethod.getSignature().equals(src_tar_sig)) {
                // 第一次修改，所有语句中的调用方法还是原方法
                // 此处使用 midMethod 和 tarMethod的原始signature区分其返回类型
                String BReturnType = src_tar_sig.split(" ")[1];
                String CReturnType = src_mid_sig.split(" ")[1];
                // 获取parameterList
                ArrayList<Value> paraList = new ArrayList<>();
                // 先获取C的parameter list并设置为默认值
                // get the parameter list of method C and set them as default values
                String[] src_tar_para = src_tar_sig.split("\\(")[1].split("\\)")[0].split(",");
                int tarParaNum;
                if (src_tar_para[0].equals("")) {
                    tarParaNum = 0;
                } else {
                    tarParaNum = src_tar_para.length;
                }
                int allParaNum = mid_method.getParameterCount();
                for (int zp = 0; zp < allParaNum - 2 - tarParaNum; zp++) {
                    paraList.add(setDefaultValue(mid_method.getParameterType(zp), body));
                }
                for (int zpl = 0; zpl < stmt.getInvokeExpr().getArgCount(); zpl++) {
                    paraList.add(stmt.getInvokeExpr().getArg(zpl));
                }
                if (Modifier.isStatic(tar_method.getModifiers())) {
                    paraList.add(NullConstant.v());
                } else {
                    int paraLeng = stmt.getInvokeExpr().getUseBoxes().size();
                    paraList.add(stmt.getInvokeExpr().getUseBoxes().get(paraLeng - 1).getValue());
                }
                paraList.add(IntConstant.v(0));
                // 调用C，类型判断
                if (BReturnType.equals("void") || !(stmt instanceof AssignStmt)) {
                    // 直接调用 C 并传入参数即可
                    if (mid_method.isStatic()) {
                        // 如果mid method (C) 是static
                        InvokeExpr invokeExpr = Jimple.v().newStaticInvokeExpr(mid_method.makeRef(),
                                paraList);
                        InvokeStmt invokeStmt = Jimple.v().newInvokeStmt(invokeExpr);
                        tgtStmt.add(invokeStmt);
                        patchMap.put(stmt, tgtStmt);
                    } else if (!src_method.getDeclaringClass().getName().equals(
                            mid_method.getDeclaringClass().getName())) {
                        // A C 不在同一个类中
                        Local callC = lg.generateLocal(mid_method.getDeclaringClass().getType());
                        NewExpr callObj = Jimple.v().newNewExpr(RefType.v(mid_method.getDeclaringClass()));
                        AssignStmt aStmt = Jimple.v().newAssignStmt(callC, callObj);
                        tgtStmt.add(aStmt);
                        SootMethod ctm = null;
                        for (SootMethod sm : mid_method.getDeclaringClass().getMethods()) {
                            if (sm.getName().contains("<init>")) {
                                if (sm.getParameterCount() == 0) {
                                    ctm = sm;
                                    break;
                                }
                            }
                        }
                        if (ctm == null) {
                            for (SootMethod sm : mid_method.getDeclaringClass().getMethods()) {
                                if (sm.getName().contains("<init>")) {
                                    ctm = sm;
                                    break;
                                }
                            }
                        }
//                        if (ctm == null){
//                            ctm = createNoneParaInitMethod(mid_method.getDeclaringClass());
//                        }
                        make_method_accessible(ctm);
                        ArrayList<Value> pl = new ArrayList<>();
                        for (int ziii = 0; ziii < ctm.getParameterCount(); ziii++) {
                            pl.add(setDefaultValue(ctm.getParameterType(ziii), body));
                        }
                        InvokeExpr ie = Jimple.v().newSpecialInvokeExpr(callC,
                                ctm.makeRef(),
                                pl);
//                        }
                        Stmt t1 = Jimple.v().newInvokeStmt(ie);
                        tgtStmt.add(t1);
                        // 用该对象调用
                        InvokeExpr invokeExpr_1 = Jimple.v().newVirtualInvokeExpr(callC,
                                mid_method.makeRef(), paraList);
                        Stmt stmt_2 = Jimple.v().newInvokeStmt(invokeExpr_1);
                        tgtStmt.add(stmt_2);
                        patchMap.put(stmt, tgtStmt);
//                        getInitMethod(mid_method.getDeclaringClass(), tgtStmt,lg);
                    } else {
                        // A C 在同一类中
                        Local thisLocal = body.getThisLocal();
                        InvokeExpr invokeExpr = Jimple.v().newVirtualInvokeExpr(thisLocal,
                                mid_method.makeRef(), paraList);
                        InvokeStmt invokeStmt = Jimple.v().newInvokeStmt(invokeExpr);
                        tgtStmt.add(invokeStmt);
                        patchMap.put(stmt, tgtStmt);
                    }

                } else if (BReturnType.equals(CReturnType) | CReturnType.equals("void")) {
                    // 处理 B 返回类型不为空的情况1： B C 返回类型相同，或C返回类型为空
                    // 直接将invoke语句的后半部分对应替换为C即可
                    // 获取保存B的返回值的local
                    if (mid_method.isStatic()) {
                        // 调用mid
                        InvokeExpr invokeExpr = Jimple.v().newStaticInvokeExpr(mid_method.makeRef(),
                                paraList);
                        if (stmt instanceof AssignStmt || stmt instanceof JAssignStmt) {
                            Local lo = (Local) ((JAssignStmt) stmt).getLeftOp();
                            AssignStmt assignStmt = Jimple.v().newAssignStmt(lo, invokeExpr);
                            tgtStmt.add(assignStmt);
                        } else {
                            InvokeStmt invokeStmt = Jimple.v().newInvokeStmt(invokeExpr);
                            tgtStmt.add(invokeStmt);
                        }
                        patchMap.put(stmt, tgtStmt);
                    } else if (!src_method.getDeclaringClass().getName().equals(
                            mid_method.getDeclaringClass().getName()) || Modifier.isStatic(src_method.getModifiers())) {
                        // A C 不在一个类中 或 A是static
                        Local callC = lg.generateLocal(mid_method.getDeclaringClass().getType());
                        NewExpr callObj = Jimple.v().newNewExpr(RefType.v(mid_method.getDeclaringClass()));
                        AssignStmt assignStmt = Jimple.v().newAssignStmt(callC, callObj);
                        tgtStmt.add(assignStmt);
                        // 初始化调用C所需的对象
                        SootMethod ctm = null;
                        for (SootMethod sm : mid_method.getDeclaringClass().getMethods()) {
                            if (sm.getName().contains("<init>")) {
                                if (sm.getParameterCount() == 0) {
                                    ctm = sm;
                                    break;
                                }
                            }
                        }
                        if (ctm == null) {
                            for (SootMethod sm : mid_method.getDeclaringClass().getMethods()) {
                                if (sm.getName().contains("<init>")) {
                                    ctm = sm;
                                    break;
                                }
                            }
                        }
                        ArrayList<Value> pl = new ArrayList<>();
                        for (int ziii = 0; ziii < ctm.getParameterCount(); ziii++) {
                            pl.add(setDefaultValue(ctm.getParameterType(ziii), body));
                        }
                        InvokeExpr invokeExpr_initC = Jimple.v().newSpecialInvokeExpr(callC,
                                ctm.makeRef(), pl);

                        Stmt stmt_initC = Jimple.v().newInvokeStmt(invokeExpr_initC);
                        tgtStmt.add(stmt_initC);
                        // 调用C
                        make_method_accessible(mid_method);
                        InvokeExpr invokeExpr_2 = Jimple.v().newVirtualInvokeExpr(callC,
                                mid_method.makeRef(), paraList);
                        if (stmt instanceof AssignStmt || stmt instanceof JAssignStmt) {
                            Local lo = (Local) ((JAssignStmt) stmt).getLeftOp();
                            AssignStmt assignStmt2 = Jimple.v().newAssignStmt(lo, invokeExpr_2);
                            tgtStmt.add(assignStmt2);
                        } else {
                            InvokeStmt invokeStmt = Jimple.v().newInvokeStmt(invokeExpr_2);
                            tgtStmt.add(invokeStmt);
                        }
                        patchMap.put(stmt, tgtStmt);
                    } else {
                        // A C 在一个类中
                        Local same_class = null;
                        same_class = body.getThisLocal();

                        InvokeExpr invokeExpr = Jimple.v().newVirtualInvokeExpr(same_class,
                                mid_method.makeRef(), paraList);

                        if (stmt instanceof AssignStmt || stmt instanceof JAssignStmt) {
                            Local lo = (Local) ((JAssignStmt) stmt).getLeftOp();
                            AssignStmt assignStmt2 = Jimple.v().newAssignStmt(lo, invokeExpr);
                            tgtStmt.add(assignStmt2);
                        } else {
                            InvokeStmt invokeStmt = Jimple.v().newInvokeStmt(invokeExpr);
                            tgtStmt.add(invokeStmt);
                        }
                        patchMap.put(stmt, tgtStmt);
                    }
                } else {
                    // B C 返回类型都不为空，且不相同
                    // 获取保存B的返回值的local
                    Local lo = (Local) ((JAssignStmt) stmt).getLeftOp();
                    // new 一个MidType的对象，用于存储返回值，然后，将其中于B对应的部分获取
                    Local midType = lg.generateLocal(MidType.getType());
                    // 调用 C 并将返回值存到midType
                    InvokeExpr invokeC = null;
                    if (mid_method.isStatic()) {
                        invokeC = Jimple.v().newStaticInvokeExpr(mid_method.makeRef(),
                                paraList);
                    } else if ((!src_method.getDeclaringClass().getName().equals(
                            mid_method.getDeclaringClass().getName())) || (src_method.isStatic() && !mid_method.isStatic())) {
                        //A C 不在一个包中
                        Local callC = lg.generateLocal(mid_method.getDeclaringClass().getType());
                        NewExpr callObj = Jimple.v().newNewExpr(RefType.v(mid_method.getDeclaringClass()));
                        AssignStmt aStmt = Jimple.v().newAssignStmt(callC, callObj);
                        tgtStmt.add(aStmt);
                        SootMethod ctm = null;
                        for (SootMethod sm : mid_method.getDeclaringClass().getMethods()) {
                            if (sm.getName().contains("<init>")) {
                                if (sm.getParameterCount() == 0) {
                                    ctm = sm;
                                    break;
                                }
                            }
                        }
                        if (ctm == null) {
                            for (SootMethod sm : mid_method.getDeclaringClass().getMethods()) {
                                if (sm.getName().contains("<init>") && Modifier.isPublic(sm.getModifiers())) {
                                    ctm = sm;
                                    break;
                                }
                            }
//                            ctm = createNoneParaInitMethod(mid_method.getDeclaringClass());
                        }
                        if (ctm == null) {
                            for (SootMethod sm : mid_method.getDeclaringClass().getMethods()) {
                                if (sm.getName().contains("<init>")) {
                                    ctm = sm;
                                    break;
                                }
                            }
                        }
                        ArrayList<Value> pl = new ArrayList<>();
                        for (int ziii = 0; ziii < ctm.getParameterCount(); ziii++) {
                            pl.add(setDefaultValue(ctm.getParameterType(ziii), body));
                        }
                        InvokeExpr ie = Jimple.v().newSpecialInvokeExpr(callC,
                                ctm.makeRef(),
                                pl);
                        Stmt t1 = Jimple.v().newInvokeStmt(ie);
                        tgtStmt.add(t1);
                        // 用该对象调用
                        invokeC = Jimple.v().newVirtualInvokeExpr(callC,
                                mid_method.makeRef(), paraList);
                    } else {
                        // A C 在同一个类中
                        Local thisLocal = body.getThisLocal();
                        invokeC = Jimple.v().newVirtualInvokeExpr(thisLocal,
                                mid_method.makeRef(), paraList);
                    }
                    AssignStmt assignStmt_0 = Jimple.v().newAssignStmt(midType, invokeC);
                    tgtStmt.add(assignStmt_0);

                    // 从 midType 中取出B的部分，赋值给lo
                    InstanceFieldRef ifr = Jimple.v().newInstanceFieldRef(midType,
                            MidType.getFieldByName(getFieldNameZ(src_tar_sig)).makeRef());
                    AssignStmt assignStmt_2 = Jimple.v().newAssignStmt(lo, ifr);
                    tgtStmt.add(assignStmt_2);
                    patchMap.put(stmt, tgtStmt);
                }
                patchMap.put(stmt, tgtStmt);
            } else if (
                    sootMethod.getSignature().equals(tar_method.getSignature())) {
                // 已经被修改过一次，此时调用语句中的invoke method
                // 不再是原 tar_method的signature而是等于tar_method.getSignature
                // 此处使用 midMethod 和 tarMethod的原始signature区分其返回类型
                String BReturnType = tar_method.getReturnType().toString();
                String CReturnType = src_mid_sig.split(" ")[1];
                // 获取parameterList
                ArrayList<Value> paraList = new ArrayList<>();
                int tarParaNum = tar_method.getParameterCount();
                int allParaNum = mid_method.getParameterCount();
                for (int zp = 0; zp < allParaNum - 2 - tarParaNum; zp++) {
                    paraList.add(setDefaultValue(mid_method.getParameterType(zp), body));
                }
                for (int zpl = 0; zpl < stmt.getInvokeExpr().getArgCount(); zpl++) {
                    paraList.add(stmt.getInvokeExpr().getArg(zpl));
                }
                if (Modifier.isStatic(tar_method.getModifiers())) {
                    paraList.add(null);
                } else {
                    int paraLeng = stmt.getInvokeExpr().getUseBoxes().size();
                    paraList.add(stmt.getInvokeExpr().getUseBoxes().get(paraLeng - 1).getValue());
                }
                paraList.add(IntConstant.v(0));
                // 调用C，类型判断
                if (BReturnType.equals("void")) {
                    // 直接调用 C 并传入参数即可
                    if (mid_method.isStatic()) {
                        // 如果mid method (C) 是static
                        InvokeExpr invokeExpr = Jimple.v().newStaticInvokeExpr(mid_method.makeRef(),
                                paraList);
                        InvokeStmt invokeStmt = Jimple.v().newInvokeStmt(invokeExpr);
                        tgtStmt.add(invokeStmt);
                        patchMap.put(stmt, tgtStmt);
                    } else if (!src_method.getDeclaringClass().getName().equals(
                            mid_method.getDeclaringClass().getName())) {
                        // A C 不在同一个类中
                        Local callC = lg.generateLocal(mid_method.getDeclaringClass().getType());
                        NewExpr callObj = Jimple.v().newNewExpr(RefType.v(mid_method.getDeclaringClass()));
                        AssignStmt aStmt = Jimple.v().newAssignStmt(callC, callObj);
                        tgtStmt.add(aStmt);

                        SootMethod ctm = null;
                        for (SootMethod sm : mid_method.getDeclaringClass().getMethods()) {
                            if (sm.getName().contains("<init>")) {
                                if (sm.getParameterCount() == 0) {
                                    ctm = sm;
                                    break;
                                }
                            }
                        }
                        if (ctm == null) {
                            for (SootMethod sm : mid_method.getDeclaringClass().getMethods()) {
                                if (sm.getName().contains("<init>") && Modifier.isPublic(sm.getModifiers())) {
                                    ctm = sm;
                                    break;
                                }
                            }
                        }
                        if (ctm == null) {
                            for (SootMethod sm : mid_method.getDeclaringClass().getMethods()) {
                                if (sm.getName().contains("<init>")) {
                                    ctm = sm;
                                    break;
                                }
                            }
                        }
                        ArrayList<Value> pl = new ArrayList<>();
                        for (int ziii = 0; ziii < ctm.getParameterCount(); ziii++) {
                            pl.add(setDefaultValue(ctm.getParameterType(ziii), body));
                        }
                        InvokeExpr ie = Jimple.v().newSpecialInvokeExpr(callC,
                                ctm.makeRef(),
                                pl);
                        Stmt t1 = Jimple.v().newInvokeStmt(ie);
                        tgtStmt.add(t1);

                        // 用该对象调用
                        InvokeExpr invokeExpr_1 = Jimple.v().newVirtualInvokeExpr(callC,
                                mid_method.makeRef(), paraList);
                        Stmt stmt_2 = Jimple.v().newInvokeStmt(invokeExpr_1);
                        tgtStmt.add(stmt_2);
                        patchMap.put(stmt, tgtStmt);

                    } else {
                        // A C 在同一类中
                        Local thisLocal = body.getThisLocal();
                        InvokeExpr invokeExpr = Jimple.v().newVirtualInvokeExpr(thisLocal,
                                mid_method.makeRef(), paraList);
                        InvokeStmt invokeStmt = Jimple.v().newInvokeStmt(invokeExpr);
                        tgtStmt.add(invokeStmt);
                        patchMap.put(stmt, tgtStmt);
                    }
                } else if (BReturnType.equals(CReturnType) | CReturnType.equals("void")) {
                    // 处理 B 返回类型不为空的情况1： B C 返回类型相同，或C返回类型为空
                    // 直接将invoke语句的后半部分对应替换为C即可
                    // 获取保存B的返回值的local
                    Local lo = (Local) ((JAssignStmt) stmt).getLeftOp();
                    if (mid_method.isStatic()) {
                        // 调用mid
                        InvokeExpr invokeExpr = Jimple.v().newStaticInvokeExpr(mid_method.makeRef(),
                                paraList);
                        AssignStmt assignStmt = Jimple.v().newAssignStmt(lo, invokeExpr);
                        tgtStmt.add(assignStmt);
                        patchMap.put(stmt, tgtStmt);
                    } else if (!src_method.getDeclaringClass().getName().equals(
                            mid_method.getDeclaringClass().getName())) {
                        // A C 不在一个类中
                        Local callC = lg.generateLocal(mid_method.getDeclaringClass().getType());
                        NewExpr callObj = Jimple.v().newNewExpr(RefType.v(mid_method.getDeclaringClass()));
                        AssignStmt assignStmt = Jimple.v().newAssignStmt(callC, callObj);
                        tgtStmt.add(assignStmt);
                        // 初始化调用C所需的对象
                        SootMethod ctm = null;
                        for (SootMethod sm : mid_method.getDeclaringClass().getMethods()) {
                            if (sm.getName().contains("<init>")) {
                                if (sm.getParameterCount() == 0) {
                                    ctm = sm;
                                    break;
                                }
                            }
                        }
                        if (ctm == null) {
                            for (SootMethod sm : mid_method.getDeclaringClass().getMethods()) {
                                if (sm.getName().contains("<init>") && Modifier.isPublic(sm.getModifiers())) {
                                    ctm = sm;
                                    break;
                                }
                            }
                        }
                        if (ctm == null) {
                            for (SootMethod sm : mid_method.getDeclaringClass().getMethods()) {
                                if (sm.getName().contains("<init>")) {
                                    ctm = sm;
                                    break;
                                }
                            }
                        }
                        ArrayList<Value> pl = new ArrayList<>();
                        for (int ziii = 0; ziii < ctm.getParameterCount(); ziii++) {
                            pl.add(setDefaultValue(ctm.getParameterType(ziii), body));
                        }
                        InvokeExpr invokeExpr_initC = Jimple.v().newSpecialInvokeExpr(callC,
                                ctm.makeRef(), pl);
                        Stmt stmt_initC = Jimple.v().newInvokeStmt(invokeExpr_initC);
                        tgtStmt.add(stmt_initC);

                        // 调用C
                        make_method_accessible(mid_method);
                        InvokeExpr invokeExpr_2 = Jimple.v().newVirtualInvokeExpr(callC,
                                mid_method.makeRef(), paraList);
                        AssignStmt assignStmt_2 = Jimple.v().newAssignStmt(lo, invokeExpr_2);
                        tgtStmt.add(assignStmt_2);
                        patchMap.put(stmt, tgtStmt);
                    } else {
                        // A C 在一个类中
                        Local same_class = body.getThisLocal();
                        InvokeExpr invokeExpr = Jimple.v().newVirtualInvokeExpr(same_class,
                                mid_method.makeRef(), paraList);
                        AssignStmt assignStmt = Jimple.v().newAssignStmt(lo, invokeExpr);
                        tgtStmt.add(assignStmt);
                        patchMap.put(stmt, tgtStmt);
                    }
                } else {
                    // B C 返回类型都不为空，且不相同
                    // 获取保存B的返回值的local
                    Local lo = (Local) ((JAssignStmt) stmt).getLeftOp();
                    // new 一个MidType的对象，用于存储返回值，然后，将其中于B对应的部分获取
                    Local midType = lg.generateLocal(MidType.getType());
                    // 调用 C 并将返回值存到midType
                    InvokeExpr invokeC = null;
                    if (mid_method.isStatic()) {
                        invokeC = Jimple.v().newStaticInvokeExpr(mid_method.makeRef(),
                                paraList);
                    } else if (!src_method.getDeclaringClass().getName().equals(
                            mid_method.getDeclaringClass().getName())) {
                        //A C 不在一个包中
                        Local callC = lg.generateLocal(mid_method.getDeclaringClass().getType());
                        NewExpr callObj = Jimple.v().newNewExpr(RefType.v(mid_method.getDeclaringClass()));
                        AssignStmt aStmt = Jimple.v().newAssignStmt(callC, callObj);
                        tgtStmt.add(aStmt);
                        SootMethod ctm = null;
                        for (SootMethod sm : mid_method.getDeclaringClass().getMethods()) {
                            if (sm.getName().contains("<init>")) {
                                if (sm.getParameterCount() == 0) {
                                    ctm = sm;
                                    break;
                                }
                            }
                        }
                        if (ctm == null) {
                            for (SootMethod sm : mid_method.getDeclaringClass().getMethods()) {
                                if (sm.getName().contains("<init>") && Modifier.isPublic(sm.getModifiers())) {
                                    ctm = sm;
                                    break;
                                }
                            }
                        }
                        if (ctm == null) {
                            for (SootMethod sm : mid_method.getDeclaringClass().getMethods()) {
                                if (sm.getName().contains("<init>")) {
                                    ctm = sm;
                                    break;
                                }
                            }
                        }
                        ArrayList<Value> pl = new ArrayList<>();
                        for (int ziii = 0; ziii < ctm.getParameterCount(); ziii++) {
                            pl.add(setDefaultValue(ctm.getParameterType(ziii), body));
                        }
                        InvokeExpr ie = Jimple.v().newSpecialInvokeExpr(callC,
                                ctm.makeRef(),
                                pl);
                        Stmt t1 = Jimple.v().newInvokeStmt(ie);
                        tgtStmt.add(t1);
                        // 用该对象调用
                        invokeC = Jimple.v().newVirtualInvokeExpr(callC,
                                mid_method.makeRef(), paraList);
                    } else {
                        // A C 在同一个类中
                        Local thisLocal = body.getThisLocal();
                        invokeC = Jimple.v().newVirtualInvokeExpr(thisLocal,
                                mid_method.makeRef(), paraList);
                    }
                    AssignStmt assignStmt_0 = Jimple.v().newAssignStmt(midType, invokeC);
                    tgtStmt.add(assignStmt_0);
                    // 从 midType 中取出B的部分，赋值给lo
                    InstanceFieldRef ifr = Jimple.v().newInstanceFieldRef(midType,
                            MidType.getFieldByName(getFieldNameZ(src_tar_sig)).makeRef());
                    AssignStmt assignStmt_2 = Jimple.v().newAssignStmt(lo, ifr);
                    tgtStmt.add(assignStmt_2);
                }
                patchMap.put(stmt, tgtStmt);
            }
//            patchMap.put(stmt, tgtStmt);
            // else do nothing
        }
        for (Stmt srcStmt : patchMap.keySet()) {
            List<Stmt> tgtStmt = patchMap.get(srcStmt);
            for (Stmt stmt : tgtStmt) {
                units.insertBefore(stmt, srcStmt);
            }
            units.remove(srcStmt);
        }
//        System.out.println("=== test 递归 ===");
//        System.out.println(src_method.retrieveActiveBody());
    }


    public static void modify_allCallee_in_modifyEdge(SootMethod mid_method,
                                                      SootClass MidType,
                                                      String src_mid_sig,
                                                      String src_tar_method,
                                                      String latest_mid_sig) {
        // 找到所有调用mid_method 的方法
        // 确保传入的参数 src_mid_sig 是body invokeMethod 对应的signature
        String[] frameworkAPI = {"android.", "com.google", "java.", "javax.",
                "org.xml", "org.apache", "junit", "org.json",
                "org.w3c.dom"};
        for (SootClass sClass : Scene.v().getClasses()) {
            List<SootMethod> methods = sClass.getMethods();
            /** 若是framework api 直接跳过 **/
            String cur_packageName = sClass.getPackageName();
            int framework_flag = 0;
            for (int zf = 0; zf < frameworkAPI.length; zf++) {
                if (cur_packageName.startsWith(frameworkAPI[zf])) {
                    framework_flag = 1;
                    break;
                }
            }
            if (framework_flag == 1) {
                continue;
            }
            // deal with methods
            for (int z1 = 0; z1 < methods.size(); z1++) {
                SootMethod sootMethod = methods.get(z1);
                // 处理方法体为空的情况
                Body cur_b = null;
                try {
                    cur_b = sootMethod.retrieveActiveBody();
                } catch (Exception e) {
                    continue;
                }
                assert cur_b != null;
                //
                Body jBody = cur_b;
                PatchingChain<Unit> cUnits = cur_b.getUnits();
                HashMap<Stmt, List<Stmt>> patchMap = new HashMap<>();
                LocalGenerator lg = new LocalGenerator(jBody);
                for (Unit unit : cUnits) {
                    Stmt stmt = (Stmt) unit;
                    if (!stmt.containsInvokeExpr()) {
                        continue;
                    }
//                    if (!stmt.getInvokeExpr().getMethod().getSignature().equals(src_mid_sig)) {
//                        continue;
//                    }
                    if (stmt.getInvokeExpr().getMethod().getSignature().equals(src_mid_sig)) {
                        List<Stmt> tgtStmt = new ArrayList<>();
//                        System.out.println("==== modifying invoke method ====");
//                        System.out.println(sootMethod.getSignature());
//                        System.out.println("\t" + src_mid_sig + " ==> " + mid_method.getSignature());
                        // 获取原方法的return type
                        String midReturnType = src_mid_sig.split(" ")[1];
                        String tarMethodReturnType = src_tar_method.split(" ")[1];
                        // Step1: 获取调用原方法的参数（无论怎么修改，都需要参数）
                        ArrayList<Value> paraList = new ArrayList<>();
                        int zp;
                        for (zp = 0; zp < stmt.getInvokeExpr().getArgCount(); zp++) {
                            paraList.add(stmt.getInvokeExpr().getArg(zp));
                        }
                        for (; zp < mid_method.getParameterCount() - 1; zp++) {
                            paraList.add(setDefaultValue(mid_method.getParameterType(zp), jBody));
                        }
                        paraList.add(IntConstant.v(1));
                        // Step 2：修改调用语句，对 B C的返回值进行讨论
                        if (midReturnType.equals("void")) {
                            // 不用管返回类型，直接修改参数调用即可
                            int paraLen = stmt.getInvokeExpr().getUseBoxes().size();
                            String cur_invokeType = stmt.getInvokeExpr().toString().split(" ")[0];
                            InvokeExpr cur_invokeExpr = null;
                            if (cur_invokeType.equals("staticinvoke")) {
                                cur_invokeExpr = Jimple.v().newStaticInvokeExpr(mid_method.makeRef(), paraList);
                            } else {
                                Local cur_local = (Local) stmt.getInvokeExpr().getUseBoxes().get(paraLen - 1).getValue();
                                if (cur_invokeType.equals("specialinvoke")) {
                                    cur_invokeExpr = Jimple.v().newSpecialInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else if (cur_invokeType.equals("virtualinvoke")) {
                                    cur_invokeExpr = Jimple.v().newVirtualInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else if (cur_invokeType.equals("interfaceinvoke")) {
                                    cur_invokeExpr = Jimple.v().newInterfaceInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else {
                                    cur_invokeExpr = Jimple.v().newVirtualInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                }
                            }
                            InvokeStmt invokeStmt = Jimple.v().newInvokeStmt(cur_invokeExpr);
                            tgtStmt.add(invokeStmt);
                        } else if (tarMethodReturnType.equals("void") || !(stmt instanceof AssignStmt)) {
                            // 不用修改返回类型，直接按照原调用方法，修改参数调用即可
                            Stmt newStmt = null;
                            int paraLen = stmt.getInvokeExpr().getUseBoxes().size();
                            String cur_invokeType = stmt.getInvokeExpr().toString().split(" ")[0];
                            InvokeExpr cur_invokeExpr = null;
                            if (cur_invokeType.equals("staticinvoke")) {
                                cur_invokeExpr = Jimple.v().newStaticInvokeExpr(mid_method.makeRef(), paraList);
                            } else {
                                Local cur_local = (Local) stmt.getInvokeExpr().getUseBoxes().get(paraLen - 1).getValue();
                                if (cur_invokeType.equals("specialinvoke")) {
                                    cur_invokeExpr = Jimple.v().newSpecialInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else if (cur_invokeType.equals("virtualinvoke")) {
                                    cur_invokeExpr = Jimple.v().newVirtualInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else if (cur_invokeType.equals("interfaceinvoke")) {
                                    cur_invokeExpr = Jimple.v().newInterfaceInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else {
                                    cur_invokeExpr = Jimple.v().newVirtualInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                }
                            }
                            newStmt = Jimple.v().newInvokeStmt(cur_invokeExpr);
                            tgtStmt.add(newStmt);
                        } else if (midReturnType.equals(tarMethodReturnType) && !tarMethodReturnType.equals("void")) {
                            // 不用修改返回类型，直接按照原调用方法，修改参数调用即可
                            Local lo = (Local) ((AssignStmt) stmt).getLeftOp();
                            Stmt newStmt = null;
                            int paraLen = stmt.getInvokeExpr().getUseBoxes().size();
                            String cur_invokeType = stmt.getInvokeExpr().toString().split(" ")[0];
                            InvokeExpr cur_invokeExpr = null;
                            if (cur_invokeType.equals("staticinvoke")) {
                                cur_invokeExpr = Jimple.v().newStaticInvokeExpr(mid_method.makeRef(), paraList);
                            } else {
                                Local cur_local = (Local) stmt.getInvokeExpr().getUseBoxes().get(paraLen - 1).getValue();
                                if (cur_invokeType.equals("specialinvoke")) {
                                    cur_invokeExpr = Jimple.v().newSpecialInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else if (cur_invokeType.equals("virtualinvoke")) {
                                    cur_invokeExpr = Jimple.v().newVirtualInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else if (cur_invokeType.equals("interfaceinvoke")) {
                                    cur_invokeExpr = Jimple.v().newInterfaceInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else {
                                    cur_invokeExpr = Jimple.v().newVirtualInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                }
                            }
                            newStmt = Jimple.v().newAssignStmt(lo, cur_invokeExpr);
                            tgtStmt.add(newStmt);
                        } else {
                            // 需要MidType
                            // 获取保存B的返回值的local
                            Local lo = (Local) ((AssignStmt) stmt).getLeftOp();
                            int paraLen = stmt.getInvokeExpr().getUseBoxes().size();
                            // new 一个 MidType 对象，用于存储返回值，
                            Local midType = lg.generateLocal(MidType.getType());
                            // 调用C 并将返回值保存到midType, 然后将midtype 中 C return tyep的部分赋值给lo
                            InvokeExpr cur_invokeExpr = null;
                            String cur_invokeType = stmt.getInvokeExpr().toString().split(" ")[0];
                            if (cur_invokeType.equals("staticinvoke")) {
                                cur_invokeExpr = Jimple.v().newStaticInvokeExpr(mid_method.makeRef(), paraList);
                            } else {
                                Local cur_local = (Local) stmt.getInvokeExpr().getUseBoxes().get(paraLen - 1).getValue();
                                if (cur_invokeType.equals("specialinvoke")) {
                                    cur_invokeExpr = Jimple.v().newSpecialInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else if (cur_invokeType.equals("virtualinvoke")) {
                                    cur_invokeExpr = Jimple.v().newVirtualInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else if (cur_invokeType.equals("interfaceinvoke")) {
                                    cur_invokeExpr = Jimple.v().newInterfaceInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else {
                                    cur_invokeExpr = Jimple.v().newVirtualInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                }
                            }
                            AssignStmt assignStmt_1 = Jimple.v().newAssignStmt(midType, cur_invokeExpr);
                            tgtStmt.add(assignStmt_1);
                            // 将midType 中C returnType的部分赋值给lo
                            InstanceFieldRef ifr = Jimple.v().newInstanceFieldRef(midType,
                                    MidType.getFieldByName(getFieldNameZ(src_mid_sig)).makeRef());
                            AssignStmt assignStmt_2 = Jimple.v().newAssignStmt(lo, ifr);
                            tgtStmt.add(assignStmt_2);
                        }
                        patchMap.put(stmt, tgtStmt);
                    } else if (stmt.getInvokeExpr().getMethod().getSignature().equals(latest_mid_sig)) {
                        List<Stmt> tgtStmt = new ArrayList<>();
//                        System.out.println("==== modifying invoke method ====");
//                        System.out.println(sootMethod.getSignature());
//                        System.out.println("\t" + latest_mid_sig + " ==> " + mid_method.getSignature());
                        // 获取原方法的return type
                        String midReturnType = latest_mid_sig.split(" ")[1];
                        String tarMethodReturnType = mid_method.getReturnType().toString();
                        // Step1: 获取调用原方法的参数（无论怎么修改，都需要参数）
                        ArrayList<Value> paraList = new ArrayList<>();
                        int zp;
                        for (zp = 0; zp < stmt.getInvokeExpr().getArgCount(); zp++) {
                            paraList.add(stmt.getInvokeExpr().getArg(zp));
                        }
                        for (; zp < mid_method.getParameterCount() - 1; zp++) {
                            paraList.add(setDefaultValue(mid_method.getParameterType(zp), jBody));
                        }
                        paraList.add(IntConstant.v(1));
                        // Step 2：修改调用语句，对 B C的返回值进行讨论
                        if (midReturnType.equals("void")) {
                            // 不用管返回类型，直接修改参数调用即可
                            int paraLen = stmt.getInvokeExpr().getUseBoxes().size();
                            String cur_invokeType = stmt.getInvokeExpr().toString().split(" ")[0];
                            InvokeExpr cur_invokeExpr = null;
                            if (cur_invokeType.equals("staticinvoke")) {
                                cur_invokeExpr = Jimple.v().newStaticInvokeExpr(mid_method.makeRef(), paraList);
                            } else {
                                Local cur_local = (Local) stmt.getInvokeExpr().getUseBoxes().get(paraLen - 1).getValue();
                                if (cur_invokeType.equals("specialinvoke")) {
                                    cur_invokeExpr = Jimple.v().newSpecialInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else if (cur_invokeType.equals("virtualinvoke")) {
                                    cur_invokeExpr = Jimple.v().newVirtualInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else if (cur_invokeType.equals("interfaceinvoke")) {
                                    cur_invokeExpr = Jimple.v().newInterfaceInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else {
                                    cur_invokeExpr = Jimple.v().newVirtualInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                }
                            }
                            InvokeStmt invokeStmt = Jimple.v().newInvokeStmt(cur_invokeExpr);
                            tgtStmt.add(invokeStmt);
                            continue;
                        } else if (midReturnType.equals(tarMethodReturnType) | tarMethodReturnType.equals("void")) {
                            // 不用修改返回类型，直接按照原调用方法，修改参数调用即可
//                            Local lo = (Local) ((AssignStmt) stmt).getLeftOp();
                            Stmt newStmt = null;
                            int paraLen = stmt.getInvokeExpr().getUseBoxes().size();
                            String cur_invokeType = stmt.getInvokeExpr().toString().split(" ")[0];
                            InvokeExpr cur_invokeExpr = null;
                            if (cur_invokeType.equals("staticinvoke")) {
                                cur_invokeExpr = Jimple.v().newStaticInvokeExpr(mid_method.makeRef(), paraList);
                            } else {
                                Local cur_local = (Local) stmt.getInvokeExpr().getUseBoxes().get(paraLen - 1).getValue();
                                if (cur_invokeType.equals("specialinvoke")) {
                                    cur_invokeExpr = Jimple.v().newSpecialInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else if (cur_invokeType.equals("virtualinvoke")) {
                                    cur_invokeExpr = Jimple.v().newVirtualInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else if (cur_invokeType.equals("interfaceinvoke")) {
                                    cur_invokeExpr = Jimple.v().newInterfaceInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                } else {
                                    cur_invokeExpr = Jimple.v().newVirtualInvokeExpr(cur_local, mid_method.makeRef(), paraList);
                                }
                            }
                            if (stmt instanceof AssignStmt | stmt instanceof JAssignStmt) {
                                Local lo = (Local) ((AssignStmt) stmt).getLeftOp();
                                newStmt = Jimple.v().newAssignStmt(lo, cur_invokeExpr);
                            } else {
                                newStmt = Jimple.v().newInvokeStmt(cur_invokeExpr);
                            }
                            tgtStmt.add(newStmt);
                        }
                        patchMap.put(stmt, tgtStmt);
                    } else {
                        continue;
                    }
                }
                for (Stmt srcStmt : patchMap.keySet()) {
                    List<Stmt> tgtStmt = patchMap.get(srcStmt);
                    for (Stmt stmt : tgtStmt) {
                        cUnits.insertBefore(stmt, srcStmt);
                    }
                    cUnits.remove(srcStmt);
                }
                cur_b.validate();
                sootMethod.setActiveBody(cur_b);
            }
        }
    }


    public static void make_field_accessible(SootField sootField) {
        int zflag = sootField.getModifiers();
        if (Modifier.isPrivate(sootField.getModifiers())) {
            zflag -= Modifier.PRIVATE;
        }
        if (Modifier.isProtected(sootField.getModifiers())) {
            zflag -= Modifier.PROTECTED;
        }
        if (Modifier.isFinal(sootField.getModifiers())) {
            zflag -= Modifier.FINAL;
        }
        if (!Modifier.isPublic(sootField.getModifiers())) {
            zflag += Modifier.PUBLIC;
        }
        sootField.setModifiers(zflag);
    }


    public static List<Stmt> replace_callStmt(SootMethod caller_method, Stmt cur_stmt,
                                              SootMethod callee_method) {
        List<Stmt> replaceStmt = new ArrayList<>();
        Body calleeBody = callee_method.retrieveActiveBody();
        Body callerBody = caller_method.retrieveActiveBody();
        PatchingChain<Unit> caller_units = callerBody.getUnits();
        LocalGenerator lg = new LocalGenerator(callerBody);
        HashMap<Value, Value> paraRela = new HashMap<>();   // zkf 21-03-03 <local,local> -> <local, value>
        // zkf 2021-03-13 <local, value> -> <value, value>???
        HashMap<Stmt, Stmt> voidReturn = new HashMap<>();
        JimpleBody jBody = (JimpleBody) calleeBody.clone();
        PatchingChain<Unit> units = jBody.getUnits();
        // 找到所有 return void 语句
        if (callee_method.getReturnType() instanceof VoidType) {
            List<Stmt> tmpStmt = new ArrayList<>();
            for (Unit unit : units) {
                Stmt stmt = (Stmt) unit;
                if (stmt instanceof ReturnVoidStmt) {
//                    Local lastStmt = lg.generateLocal(IntType.v());
//                    AssignStmt assignStmt = Jimple.v().newAssignStmt(lastStmt, IntConstant.v(1));
                    tmpStmt.add(stmt);
                }
            }
            for (int zi = 0; zi < tmpStmt.size(); zi++) {
                Stmt stmt = tmpStmt.get(zi);
                Local lastStmt = lg.generateLocal(IntType.v());
                AssignStmt assignStmt = Jimple.v().newAssignStmt(lastStmt, IntConstant.v(1));
                units.insertBefore(assignStmt, stmt);
                voidReturn.put(stmt, assignStmt);
            }
        }
        //获取调用对象，即callee中的this
        Local callObj = null;
        if (Modifier.isStatic(callee_method.getModifiers()) && !(cur_stmt.getInvokeExpr() instanceof StaticInvokeExpr)) {
            //zkf 2021-03-03 && !(cur_stmt.getInvokeExpr() instanceof StaticInvokeExpr) deal with staticIvoke
            // 如果该方法是static的，则调用方法不需要目标类对象，但在目标方法中，调用需要该类的this可能
            if (caller_method.getDeclaringClass().getName().equals(
                    callee_method.getDeclaringClass().getName()//在同一个类中
            )) {
                callObj = callerBody.getThisLocal();
            } else {
                // 声明目标类对象 并初始化
                callObj = lg.generateLocal(callee_method.getDeclaringClass().getType());
                NewExpr callObjTmp = Jimple.v().newNewExpr(RefType.v(callee_method.getDeclaringClass()));
                AssignStmt assignStmt = Jimple.v().newAssignStmt(callObj, callObjTmp);
                replaceStmt.add(assignStmt);
                SootMethod ctm = null;
                for (SootMethod sm : callee_method.getDeclaringClass().getMethods()) {
                    if (sm.getName().contains("<init>")) {
                        if (sm.getParameterCount() == 0) {
                            ctm = sm;
                            break;
                        }
                    }
                }
                if (ctm == null) {
                    for (SootMethod sm : callee_method.getDeclaringClass().getMethods()) {
                        if (sm.getName().contains("<clinit>")) {
                            ctm = sm;
                            break;
                        }
                    }
                }
                if (ctm != null) { // zkf 2021-03-03
                    make_method_accessible(ctm);
                    ArrayList<Value> pl = new ArrayList<>();
                    for (int ziii = 0; ziii < ctm.getParameterCount(); ziii++) {
                        pl.add(setDefaultValue(ctm.getParameterType(ziii), calleeBody));
                    }
                    InvokeExpr ie = Jimple.v().newSpecialInvokeExpr(callObj,
                            ctm.makeRef(),
                            pl);
                    Stmt t1 = Jimple.v().newInvokeStmt(ie);
                    replaceStmt.add(t1);
                } else if (Modifier.isStatic(callee_method.getModifiers())) { // zkf 2021-03-03 , callee 是static 方法，可直接调用的情况
                    //do nothing
                }

            }
        } else if (!(cur_stmt.getInvokeExpr() instanceof StaticInvokeExpr)) {
            int paraLeng = cur_stmt.getInvokeExpr().getUseBoxes().size();
            // zkf 2021-03-03 处理最后一个参数是instance
//            if ( !( cur_stmt.getInvokeExpr().getUseBoxes().get(paraLeng - 1).getValue() instanceof  Constant)){
//                callObj = (Local) cur_stmt.getInvokeExpr().getUseBoxes().get(paraLeng - 1).getValue();
//            }else{
//                callObj = lg.generateLocal(cur_stmt.getInvokeExpr().getUseBoxes().get(paraLeng - 1).getValue().getType());
//                AssignStmt assignStmt = Jimple.v().newAssignStmt(callObj,
//                        cur_stmt.getInvokeExpr().getUseBoxes().get(paraLeng - 1).getValue());
//                replaceStmt.add(assignStmt);
//            }
            // zkf 2021-03-03 处理最后一个参数是instance
//            callObj = lg.generateLocal(cur_stmt.getInvokeExpr().getUseBoxes().get(paraLeng - 1).getValue().getType());
            callObj = (Local) cur_stmt.getInvokeExpr().getUseBoxes().get(paraLeng - 1).getValue();
//            AssignStmt assignStmt = Jimple.v().newAssignStmt(callObj,
//                    cur_stmt.getInvokeExpr().getUseBoxes().get(paraLeng - 1).getValue());
//            replaceStmt.add(assignStmt);
        }
        // 获取返回类型
        Local returnValue = null;
        int flag_assign = 0;
//        if (!(callee_method.getReturnType() instanceof VoidType)) {
////        if ((callee_method.getReturnType() instanceof AssignStmt)) {
//            returnValue = (Local) ((JAssignStmt) cur_stmt).getLeftOp();
//            flag_assign = 1;
//        }
        // zkf 2021-03-12
        if (cur_stmt instanceof JAssignStmt) {
            returnValue = (Local) ((JAssignStmt) cur_stmt).getLeftOp();
            flag_assign = 1;
        }
        // 获取参数列表
        int paraCount = callee_method.getParameterCount();
        List<Value> paralist = new ArrayList<>(); // zkf 2021-03-03 Local -> Value
        if (paraCount == 0) {
            paralist = null;
        } else {
            for (int zp = 0; zp < cur_stmt.getInvokeExpr().getArgCount(); zp++) {
                if (cur_stmt.getInvokeExpr().getArg(zp) instanceof Constant) {
//                    // zkf 2021-03-03 实际上如果是instance 直接给值就好 注释 03-05 投入使用
                    Local z1 = lg.generateLocal(cur_stmt.getInvokeExpr().getArg(zp).getType());
                    AssignStmt assignStmt = Jimple.v().newAssignStmt(z1, cur_stmt.getInvokeExpr().getArg(zp));
                    replaceStmt.add(assignStmt);
                    paralist.add(z1);
                    //zkf 21-03-03 add 21-03-05 delete
//                    paralist.add(cur_stmt.getInvokeExpr().getArg(zp));
                } else {
                    paralist.add(cur_stmt.getInvokeExpr().getArg(zp));
                }
//                paralist.add((Local) cur_stmt.getInvokeExpr().getArg(zp));
            }
        }
        int count = 0;
        List<Stmt> targetList = new ArrayList<>();
        for (Unit unit : units) {
            Stmt stmt = (Stmt) unit;
            if (stmt instanceof IfStmt || stmt instanceof GotoStmt) {
                targetList.add(stmt);
            }
        }
        // 开始修改
        int zFlagTarget = 0;
        int flagGotoThrowOrException = 0;
        int index = -1;
        for (Unit unit : units) {
            zFlagTarget = 0;
            Stmt stmt = (Stmt) unit;
//            if (targetList.contains(stmt)) {
//                zFlagTarget = 1;
//                index = targetList.indexOf(stmt);
//            }
            if (flagGotoThrowOrException == 1) { // 处理 goto target 为 throw/exception语句，使其goto到下一条语句
                zFlagTarget = 1;
                flagGotoThrowOrException = 0;
            }
            if (zFlagTarget == 0) {
                index = -1;
                for (Stmt tmp : targetList) {
                    index += 1;
                    if (tmp instanceof IfStmt) {
                        if (((JIfStmt) tmp).getTarget().equals(stmt)) {
                            zFlagTarget = 1;
//                    index = targetList.indexOf(stmt);
                            break;
                        }
                    }
                    if (tmp instanceof GotoStmt) {
                        if (((JGotoStmt) tmp).getTarget().equals(stmt)) {
                            zFlagTarget = 1;
//                    index = targetList.indexOf(stmt);
                            break;
                        }
                    }
                }
            }
            if (stmt instanceof ThrowStmt) {// 暂不处理try catch 语句
                if (zFlagTarget == 1) {
                    flagGotoThrowOrException = 1;
                }
                continue;
            } else if (stmt instanceof IdentityStmt) {
                if (((IdentityStmt) stmt).getRightOp() instanceof ThisRef) {
                    Local tmp = (Local) ((IdentityStmt) stmt).getLeftOp();
                    paraRela.put(tmp, callObj);
                } else {
                    Local tmp = (Local) ((IdentityStmt) stmt).getLeftOp();
                    if (paralist != null && paralist.size() > count) {
                        paraRela.put(tmp, paralist.get(count));
                    } else {
                        if (!(((IdentityStmt) stmt).getRightOp() instanceof CaughtExceptionRef)) { // zkf 21-03-03 if catch exception, just drop the stmt

                            Local t1 = lg.generateLocal(((IdentityStmt) stmt).getRightOp().getType());
                            IdentityStmt identityStmt = Jimple.v().newIdentityStmt(t1, ((IdentityStmt) stmt).getRightOp());
                            replaceStmt.add(identityStmt);
                            paraRela.put(tmp, t1);
                        } else {
                            if (zFlagTarget == 1) {
                                flagGotoThrowOrException = 1;
                            }
                        }
                    }
                    count += 1;
                }
            } else if (stmt.containsInvokeExpr()) { // 如果当前语句包含调用语句
                // 如果是用this，或para中的某个对象调用的，替换
                if (stmt.getInvokeExpr() instanceof StaticInvokeExpr) {
                    if (stmt instanceof AssignStmt) {
                        // 如果当前语句是 assign语句
                        if (((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().size() > 0) {
                            // zkf 2021-03-02
//                            List<ValueBox> temp = ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes();
//                            for (int i=0; i< temp.size();i++){
//                                ValueBox tmp = temp.get(i);
//                                if (tmp.getValue() instanceof Constant){
//                                    continue;
//                                } else{
//                                    if (paraRela.containsKey(tmp.getValue())) {
//                                        ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(0).setValue(paraRela.get(tmp.getValue()));
//                                    } else {
//                                        Local t = lg.generateLocal(tmp.getValue().getType());
//                                        paraRela.put((Local) tmp.getValue(), t);
//                                        ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(0).setValue(paraRela.get(tmp.getValue()));
//                                    }
//                                }
//                            }
                            // zkf 2021-03-26
                            for (int z26 = 0; z26 < ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().size(); z26++) {
                                if (!(((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(z26).getValue() instanceof Constant)) { // if added zkf 2021-03-03
                                    Local tmp = (Local) ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(z26).getValue();
                                    if (paraRela.containsKey(tmp)) {
                                        ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(z26).setValue(paraRela.get(tmp));
                                    } else {
                                        Local t = lg.generateLocal(tmp.getType());
                                        paraRela.put(tmp, t);
                                        ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(z26).setValue(paraRela.get(tmp));
                                    }
                                }
                            }
//                            /*** zkf 2021-03-02
//                            if (!(((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(0).getValue() instanceof Constant)) { // if added zkf 2021-03-03
//                                Local tmp = (Local) ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(0).getValue();
//                                if (paraRela.containsKey(tmp)) {
//                                    ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(0).setValue(paraRela.get(tmp));
//                                } else {
//                                    Local t = lg.generateLocal(tmp.getType());
//                                    paraRela.put(tmp, t);
//                                    ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(0).setValue(paraRela.get(tmp));
//                                }
//                            }
//                             ***/
                        }
                        Value tmp = ((JAssignStmt) stmt).getLeftOp();
                        if (paraRela.containsKey(tmp)) {
                            ((JAssignStmt) stmt).setLeftOp(paraRela.get(tmp));
                        } else if (!callerBody.getLocals().contains(tmp)) {
                            Local tmp1 = lg.generateLocal(((JAssignStmt) stmt).getLeftOp().getType());
                            paraRela.put((Local) ((JAssignStmt) stmt).getLeftOp(), tmp1);
                            ((JAssignStmt) stmt).setLeftOp(tmp1);
                        }
//                        if (((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().size() > 0) {
//                            Local tmp11 = (Local) ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(0).getValue();
//                            if (paraRela.keySet().contains(tmp11)) {
//                                ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(0).setValue(paraRela.get(tmp11));
//                            } else {
//                                Local t = lg.generateLocal(tmp11.getType());
//                                paraRela.put(tmp11,t);
//                                ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(0).setValue(paraRela.get(tmp11));
//                            }
//                        }
//                        Value tmp12 = ((JAssignStmt) stmt).getLeftOp();
//                        if (!callerBody.getLocals().contains(tmp12)) {
//                            Local tmp111 = lg.generateLocal(((JAssignStmt) stmt).getLeftOp().getType());
//                            paraRela.put((Local) ((JAssignStmt) stmt).getLeftOp(), tmp111);
//                            ((JAssignStmt) stmt).setLeftOp(tmp111);
//                        }
                    } else {
                        int boxNum = stmt.getUseBoxes().size();
                        for (int zi = 0; zi < boxNum; zi++) {
                            if (stmt.getUseBoxes().get(zi).getValue() instanceof Constant) {
                                continue;
                            }
                            if (stmt.getUseBoxes().get(zi).getValue() instanceof InvokeExpr) {
                                continue;
                            }
                            Local tmppp = (Local) stmt.getUseBoxes().get(zi).getValue();
                            if (paraRela.containsKey(tmppp)) {
                                stmt.getUseBoxes().get(zi).setValue(paraRela.get(tmppp));
                            } else {
                                Local t = lg.generateLocal(tmppp.getType());
                                paraRela.put(tmppp, t);
                                stmt.getUseBoxes().get(zi).setValue(paraRela.get(tmppp));
                            }
                        }
                    }
                    replaceStmt.add(stmt);
                    if (zFlagTarget == 1) {
//                        targetList.set(index, stmt);
                        for (Stmt tt : replaceStmt) {
                            if (tt instanceof IfStmt) {
                                if (((IfStmt) tt).equals(targetList.get(index))) {
                                    ((IfStmt) tt).setTarget(stmt);
                                }
                            }
                            if (tt instanceof GotoStmt) {
                                if (((GotoStmt) tt).equals(targetList.get(index))) {
                                    ((GotoStmt) tt).setTarget(stmt);
                                }
                            }
                        }
                    }
                } else {// 该方法不是static调用
                    // 获取调用？
                    int paraLeng = stmt.getInvokeExpr().getUseBoxes().size();
                    Local tmp = (Local) stmt.getInvokeExpr().getUseBoxes().get(paraLeng - 1).getValue();
                    if (paraRela.containsKey(tmp)) {
//                        if (paraRela.get(tmp) instanceof NullConstant){
//                            SootMethod sootMethod = stmt.getInvokeExpr().getMethod();
//                            make_method_static(sootMethod);
//                            StaticInvokeExpr staticInvokeExpr = Jimple.v().newStaticInvokeExpr(sootMethod.makeRef(),
//                                    stmt.getInvokeExpr().getArgs());
//                            ((JAssignStmt) stmt).setRightOp(staticInvokeExpr);
//
//                        }else{
                        stmt.getInvokeExpr().getUseBoxes().get(paraLeng - 1).setValue(paraRela.get(tmp));
//                        }
                    } else {
                        Local l = lg.generateLocal(tmp.getType());
                        paraRela.put(tmp, l);
                        stmt.getInvokeExpr().getUseBoxes().get(paraLeng - 1).setValue(paraRela.get(tmp));
                    }
                    List<Value> para = stmt.getInvokeExpr().getArgs();
                    for (int zi = 0; zi < para.size(); zi++) {
                        if (paraRela.containsKey(para.get(zi))) {
                            stmt.getInvokeExpr().setArg(zi, paraRela.get(para.get(zi)));
                        }
                    }
                    if (stmt instanceof AssignStmt) { // 如果当前语句是 assign语句
                        if (((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().size() > 0) {
                            if (((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes() instanceof ArrayList) {
                                List Ztmp = ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes();
                                for (int zkf11 = 0; zkf11 < Ztmp.size(); zkf11++) {
                                    if (paraRela.containsKey(((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(0).getValue())) {
                                        ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(zkf11).setValue(paraRela.get(
                                                ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(0).getValue()));
                                    }
                                }
                            }
//                            Local tmp11 = (Local) ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(0).getValue();
//                            if (paraRela.containsKey(tmp11)) {
//                                ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(0).setValue(paraRela.get(tmp11));
//                            }
                        }
                        Value tmp123 = ((JAssignStmt) stmt).getLeftOp();
                        if (paraRela.containsKey(tmp123)) {
                            ((JAssignStmt) stmt).setLeftOp(paraRela.get(tmp123));
                        } else if (!callerBody.getLocals().contains(tmp123)) {
                            Local tmp13 = lg.generateLocal(((JAssignStmt) stmt).getLeftOp().getType());
                            paraRela.put((Local) ((JAssignStmt) stmt).getLeftOp(), tmp13);
                            ((JAssignStmt) stmt).setLeftOp(tmp13);
                        }
                    }
                    replaceStmt.add(stmt);
                    if (zFlagTarget == 1) {
//                        targetList.set(index, stmt);
                        for (Stmt tt : replaceStmt) {
                            if (tt instanceof IfStmt) {
                                if (((IfStmt) tt).equals(targetList.get(index))) {
                                    ((IfStmt) tt).setTarget(stmt);
                                }
                            }
                            if (tt instanceof GotoStmt) {
                                if (((GotoStmt) tt).equals(targetList.get(index))) {
                                    ((GotoStmt) tt).setTarget(stmt);
                                }
                            }
                        }
                    }
                }
            } else if (stmt instanceof ReturnStmt) { // 如果当前语句是return语句
                Value getReturnValue = ((ReturnStmt) stmt).getOpBox().getValue();
                if (paraRela.containsKey(getReturnValue)) {
                    getReturnValue = paraRela.get(getReturnValue);
                }
                if (flag_assign == 1) {
                    AssignStmt assignStmt = Jimple.v().newAssignStmt(returnValue, getReturnValue);

                    replaceStmt.add(assignStmt);

                    if (zFlagTarget == 1) {
//                        targetList.set(index, stmt);
                        for (Stmt tt : replaceStmt) {
                            if (tt instanceof IfStmt) {
                                if (((IfStmt) tt).equals(targetList.get(index))) {
                                    ((IfStmt) tt).setTarget(stmt);
                                }
                            }
                            if (tt instanceof GotoStmt) {
                                if (((GotoStmt) tt).equals(targetList.get(index))) {
                                    ((GotoStmt) tt).setTarget(stmt);
                                }
                            }
                        }
                    }
                }
//                if (!stmt.equals(units.getLast())) {
//                    replaceStmt.add(Jimple.v().newReturnVoidStmt());
//                }
                continue;
            } else if (stmt instanceof ReturnVoidStmt) {
                if (!stmt.equals(units.getLast())) {
                    ReturnVoidStmt returnVoidStmt = Jimple.v().newReturnVoidStmt();
                    replaceStmt.add(returnVoidStmt);
                    if (zFlagTarget == 1) {
//                        targetList.set(index, stmt);
                        for (Stmt tt : replaceStmt) {
                            if (tt instanceof IfStmt) {
                                if (((IfStmt) tt).equals(targetList.get(index))) {
                                    ((IfStmt) tt).setTarget(stmt);
                                }
                            }
                            if (tt instanceof GotoStmt) {
                                if (((GotoStmt) tt).equals(targetList.get(index))) {
                                    ((GotoStmt) tt).setTarget(stmt);
                                }
                            }
                        }
                    }
                }
                continue;
            } else if (stmt instanceof AssignStmt) { // 如果当前语句是 assign语句
                if (((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().size() > 0) {
                    //  rightbox是 a*b， a+b,a[b]等
//                    Local tmp = (Local) ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(0).getValue();
//                    if (paraRela.keySet().contains(tmp)) {
//                        ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(0).setValue(paraRela.get(tmp));
//                    }
                    int pn = ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().size();
                    for (int zi = 0; zi < pn; zi++) {
                        if (((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(zi).getValue() instanceof Constant) {
                            continue;
                        }
                        Local leftLocal = null;
                        if (((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(zi).getValue() instanceof JInstanceFieldRef) {
                            leftLocal = (Local) (((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(zi).getValue().getUseBoxes().get(0).getValue());
                            if (paraRela.containsKey(leftLocal)) {
                                ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(zi).getValue().getUseBoxes().get(0).setValue(paraRela.get(leftLocal));
                            } else {
                                Local tar = (Local) ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(zi).getValue().getUseBoxes().get(0).getValue();
                                Local t = lg.generateLocal(tar.getType());
                                paraRela.put(tar, t);
                                ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(zi).getValue().getUseBoxes().get(0).setValue(t);

                            }
                        } else if (paraRela.containsKey(
                                ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(zi).getValue())) {
                            ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(zi).setValue(
                                    paraRela.get(
                                            ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(zi).getValue()));
                        } else {
                            Local tar = (Local) ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(zi).getValue();
                            Local t = lg.generateLocal(tar.getType());
                            paraRela.put(tar, t);
                            ((JAssignStmt) stmt).getRightOpBox().getValue().getUseBoxes().get(zi).setValue(t);
                        }
                    }
                }
                if (((JAssignStmt) stmt).getRightOpBox().getValue() instanceof Local) {
                    Local zt = (Local) ((JAssignStmt) stmt).getRightOpBox().getValue();
                    if (paraRela.containsKey(zt)) {
                        ((JAssignStmt) stmt).getRightOpBox().setValue(paraRela.get(zt));
                    } else {
                        Local t = lg.generateLocal(zt.getType());
                        paraRela.put(zt, t);
                        ((JAssignStmt) stmt).getRightOpBox().setValue(t);
                    }
                }
                Value tmp = ((JAssignStmt) stmt).getLeftOp();
                if (paraRela.containsKey(tmp)) {
                    ((JAssignStmt) stmt).setLeftOp(paraRela.get(tmp));
                } else if (!callerBody.getLocals().contains(tmp)) {
                    Local tmp1 = lg.generateLocal(((JAssignStmt) stmt).getLeftOp().getType());
                    Value leftLocal = null; // zkf 2021-03-13 Local -> Value
                    if (((JAssignStmt) stmt).getLeftOp() instanceof JInstanceFieldRef) {

                        leftLocal = (Local) ((JAssignStmt) stmt).getLeftOp().getUseBoxes().get(0).getValue();
                        if (paraRela.containsKey(leftLocal)) {
                            ((JAssignStmt) stmt).getLeftOp().getUseBoxes().get(0).setValue(paraRela.get(leftLocal));
                        } else {
                            paraRela.put(leftLocal, tmp1);
                            ((JAssignStmt) stmt).getLeftOp().getUseBoxes().get(0).setValue(tmp1);
                        }
                    }
//                    else if (((JAssignStmt) stmt).getLeftOp() instanceof StaticFieldRef) {
                    //2021-03-02
//                        Local zkf = lg.generateLocal(((JAssignStmt) stmt).getLeftOp().getType());
//                        AssignStmt assignStmt = Jimple.v().newAssignStmt(zkf, ((JAssignStmt) stmt).getLeftOp());
//                        replaceStmt.add(assignStmt);
//                        ((JAssignStmt) stmt).getLeftOp().setValue(tmp1);

//                    }
                    else {
                        leftLocal = ((JAssignStmt) stmt).getLeftOp();
                        paraRela.put(leftLocal, tmp1);
                        ((JAssignStmt) stmt).setLeftOp(tmp1);
                    }
//                    paraRela.put(leftLocal, tmp1);
//                    ((JAssignStmt) stmt).setLeftOp(tmp1);
                }
                replaceStmt.add(stmt);
                if (zFlagTarget == 1) {
//                        targetList.set(index, stmt);
                    for (Stmt tt : replaceStmt) {
                        if (tt instanceof IfStmt) {
                            if (((IfStmt) tt).equals(targetList.get(index))) {
                                ((IfStmt) tt).setTarget(stmt);
                            }
                        }
                        if (tt instanceof GotoStmt) {
                            if (((GotoStmt) tt).equals(targetList.get(index))) {
                                ((GotoStmt) tt).setTarget(stmt);
                            }
                        }
                    }
                }
            } else {

                if (stmt instanceof IfStmt) {
                    if (voidReturn.containsKey(((IfStmt) stmt).getTarget())) {
                        ((IfStmt) stmt).setTarget(voidReturn.get(((IfStmt) stmt).getTarget()));
                    }
                }
                if (stmt instanceof GotoStmt) {
                    if (voidReturn.containsKey(((GotoStmt) stmt).getTarget())) {
                        ((GotoStmt) stmt).setTarget(voidReturn.get(((GotoStmt) stmt).getTarget()));
                    }
                }
                //其他语句，比如equal语句、if语句
                int boxNum = stmt.getUseBoxes().size();
                for (int zb = 0; zb < boxNum; zb++) {
                    if (stmt.getUseBoxes().get(zb).getValue() instanceof Constant) {
                        continue;
                    }
                    if (stmt.getUseBoxes().get(zb).getValue() instanceof JEqExpr) {
                        JEqExpr expr = (JEqExpr) stmt.getUseBoxes().get(zb).getValue();
                        if (paraRela.containsKey(expr.getOp1())) {
                            expr.setOp1(paraRela.get(expr.getOp1()));
                        }
                        if (paraRela.containsKey(expr.getOp2())) {
                            expr.setOp1(paraRela.get(expr.getOp2()));
                        }
                        continue;
                    }
                    if (stmt.getUseBoxes().get(zb).getValue() instanceof JGeExpr) {
                        JGeExpr expr = (JGeExpr) stmt.getUseBoxes().get(zb).getValue();
                        if (paraRela.containsKey(expr.getOp1())) {
                            expr.setOp1(paraRela.get(expr.getOp1()));
                        }
                        if (paraRela.containsKey(expr.getOp2())) {
                            expr.setOp1(paraRela.get(expr.getOp2()));
                        }
                        continue;
                    }
                    if (paraRela.containsKey(stmt.getUseBoxes().get(zb).getValue())) {
                        stmt.getUseBoxes().get(zb).setValue(paraRela.get(stmt.getUseBoxes().get(zb).getValue()));
                    }
                }
                replaceStmt.add(stmt);
                if (zFlagTarget == 1) {
//                    targetList.set(index, stmt);
                    for (Stmt tt : replaceStmt) {
                        if (tt instanceof IfStmt) {
                            if (((IfStmt) tt).equals(targetList.get(index))) {
                                ((IfStmt) tt).setTarget(stmt);
                            }
                        }
                        if (tt instanceof GotoStmt) {
                            if (((GotoStmt) tt).equals(targetList.get(index))) {
                                ((GotoStmt) tt).setTarget(stmt);
                            }
                        }
                    }
                }
            }
        }
//        Local lastStmt = lg.generateLocal(IntType.v());
//        AssignStmt assignStmt = Jimple.v().newAssignStmt(lastStmt, IntConstant.v(1));
//        replaceStmt.add(assignStmt);
        if (targetList.size() > 0) {
            int countz = 0;
            for (Unit unit : replaceStmt) {
                Stmt stmt = (Stmt) unit;
                if (stmt instanceof IfStmt) {
                    Stmt tmp = targetList.get(countz);
                    ((IfStmt) stmt).setTarget(tmp);
                    countz++;
                    if (countz > targetList.size()) {
                        break;
                    }
                }
            }
        }
        return replaceStmt;
    }


    public static void getGraphNodesSha256(String sha256, String apk_path, String savepath) {
        String apk_file = apk_path + "/" + sha256 + ".apk";
        String node_file = savepath + "/" + sha256 + "_testNodes.txt";
        String graph_file = savepath + "/" + sha256 + "_testGraph.txt";
        String cons_file = savepath + "/" + sha256 + "_testCons.txt";
        //
        extractGraphNodesCons(apk_file, graph_file,
                node_file, cons_file);
        //

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


    public static SootMethod insert_new_nodes(SootMethod caller, String packageName, String className, String methodName) {
        if (className.equals("")) {
            className = "zkfclass";
        }
        SootClass sootClass = null;
        if (!Scene.v().containsClass(className)) {
            sootClass = new SootClass(className, Modifier.PUBLIC);
            sootClass.setSuperclass(Scene.v().getSootClass("java.lang.Object"));
            sootClass.setApplicationClass();
            sootClass.setInScene(true);
        } else {
            sootClass = Scene.v().getSootClass(className);
        }
//        String methodName = "zkf" + node_idx;
        //新建方法
        SootMethod newMehtod = new SootMethod(methodName, null,
                IntType.v(), Modifier.PUBLIC | Modifier.STATIC);
        sootClass.addMethod(newMehtod);
        Body newBody = Jimple.v().newBody();
        newBody = (JimpleBody) newBody;
        // 添加数学计算
        PatchingChain units = newBody.getUnits();
        LocalGenerator add_lg = new LocalGenerator(newBody);
        Local llr = add_lg.generateLocal(IntType.v());
        AssignStmt assignStmt = Jimple.v().newAssignStmt(llr, IntConstant.v(1));
        LocalGenerator add_lg1 = new LocalGenerator(newBody);
        Local llr1 = add_lg1.generateLocal(IntType.v());
        AssignStmt assignStmt1 = Jimple.v().newAssignStmt(llr1, IntConstant.v(1));
        AddExpr expr = Jimple.v().newAddExpr(llr, llr1);
        Local llr2 = add_lg.generateLocal(IntType.v());
        AssignStmt assignStmt2 = Jimple.v().newAssignStmt(llr2,
                expr);
        ReturnStmt rt = Jimple.v().newReturnStmt(llr2);
        units.add(assignStmt);
        units.add(assignStmt1);
        units.add(assignStmt2);
        units.add(rt);
        newBody.setMethod(newMehtod);
        newBody.validate();
        newMehtod.setActiveBody(newBody);

        Body callerBody = caller.retrieveActiveBody();
        JimpleBody jBody = (JimpleBody) callerBody;

        PatchingChain callerUnits = jBody.getUnits();

        // 创建变量获取目标函数返回值
        LocalGenerator lg = new LocalGenerator(jBody);
        Local l_int = lg.generateLocal(IntType.v());
        InvokeExpr invokeExpr = Jimple.v().newStaticInvokeExpr(newMehtod.makeRef());
        AssignStmt assignStmt4 = Jimple.v().newAssignStmt(l_int, invokeExpr);
        AddExpr addExpr = Jimple.v().newAddExpr(l_int, l_int);
        LocalGenerator lg2 = new LocalGenerator(jBody);
        Local l_int_2 = lg2.generateLocal(IntType.v());
        AssignStmt assignStmt5 = Jimple.v().newAssignStmt(l_int_2, addExpr);

        callerUnits.insertBefore(assignStmt5, ((JimpleBody) callerBody).getFirstNonIdentityStmt());
        callerUnits.insertBefore(assignStmt4, ((JimpleBody) callerBody).getFirstNonIdentityStmt());

        callerBody.validate();
        caller.setActiveBody(callerBody);

        return newMehtod;

    }

}
