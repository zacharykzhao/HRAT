package GraphExtraction;

import soot.G;
import soot.PackManager;
import soot.Scene;
import soot.SootClass;
import soot.options.Options;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;

public class SootEnvironment {
	
	private static String getClasspath(String apkPath, String platformPath) {
		return Scene.v().getAndroidJarPath(platformPath, apkPath);
	}
	
	public static void init(String apkPath, String platformPath, String outPutPath) throws Exception {
		// Clean up any old Soot instance we may have
		G.reset();
		
		// set soot environment
		Options.v().set_no_bodies_for_excluded(true);
		Options.v().set_allow_phantom_refs(true);
		Options.v().set_whole_program(true);
		Options.v().set_process_multiple_dex(true);
		Options.v().set_src_prec(Options.src_prec_apk_class_jimple);
//		Options.v().set_output_format(Options.output_format_none);

		// zkf 2021-03-02
		Options.v().set_output_format(Options.output_format_dex);
		//
		List<String> processList = new ArrayList<String>();
		processList.add(apkPath);
		Options.v().set_process_dir(processList);
		Options.v().set_android_jars(platformPath);
		Options.v().set_keep_line_number(false);
		Options.v().set_keep_offset(false);
		Options.v().set_throw_analysis(Options.throw_analysis_dalvik);
		Options.v().set_ignore_resolution_errors(true);
		Options.v().set_wrong_staticness(3);
//		Options.v().set

		
		Options.v().set_soot_classpath(getClasspath(apkPath, platformPath));

		Scene.v().loadNecessaryClasses();
		Options.v().set_output_dir(outPutPath);

		//zkf 2021-03-02
		PackManager.v().runPacks();

//		postInit();
	}
	
	private static void postInit() {
		// collecting
		HashSet<SootClass> pendingSet = new HashSet<SootClass>();
		for (SootClass sClass : Scene.v().getApplicationClasses()) {
			if (sClass.getName().startsWith("android.support."))
				pendingSet.add(sClass);
		}
		// changing
		for (SootClass sClass : pendingSet) {
			sClass.setLibraryClass();
		}
	}

}
