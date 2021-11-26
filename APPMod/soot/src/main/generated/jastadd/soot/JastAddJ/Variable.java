package soot.JastAddJ;

import java.util.HashSet;
import java.io.File;
import java.util.*;
import beaver.*;
import java.util.ArrayList;
import java.util.zip.*;
import java.io.*;
import java.io.FileNotFoundException;
import java.util.Collection;
import soot.*;
import soot.util.*;
import soot.jimple.*;
import soot.coffi.ClassFile;
import soot.coffi.method_info;
import soot.coffi.CONSTANT_Utf8_info;
import soot.tagkit.SourceFileTag;
import soot.coffi.CoffiMethodSource;
/**
  * @ast interface
 * 
 */
public interface Variable {

		 
		String name();

		 
		TypeDecl type();

		 
		Collection<TypeDecl> throwTypes();

		 
		boolean isParameter();

		// 4.5.3
		 
		// 4.5.3
        boolean isClassVariable();

		 
		boolean isInstanceVariable();

		 
		boolean isMethodParameter();

		 
		boolean isConstructorParameter();

		 
		boolean isExceptionHandlerParameter();

		 
		boolean isLocalVariable();

		// 4.5.4
		 
		// 4.5.4
        boolean isFinal();

		 
		boolean isVolatile();


		 

		boolean isBlank();

		 
		boolean isStatic();

		 
		boolean isSynthetic();


		 

		TypeDecl hostType();


		 

		Expr getInit();

		 
		boolean hasInit();


		 

		Constant constant();


		 

		Modifiers getModifiers();
  /**
   * @attribute syn
   * @aspect SourceDeclarations
   * @declaredat /Users/eric/Documents/workspaces/clara-soot/JastAddJ/Java1.5Frontend/Generics.jrag:1519
   */
  @SuppressWarnings({"unchecked", "cast"})
  Variable sourceVariableDecl();
}
