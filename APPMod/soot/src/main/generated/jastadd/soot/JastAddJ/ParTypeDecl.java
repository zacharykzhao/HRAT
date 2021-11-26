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
public interface ParTypeDecl extends Parameterization {

    //syn String name();
     
    //syn String name();
    int getNumArgument();

     
    Access getArgument(int index);

     
    String typeName();

     
    SimpleSet localFields(String name);

     
    HashMap localMethodsSignatureMap();
TypeDecl substitute(TypeVariable typeVariable);

int numTypeParameter();

TypeVariable typeParameter(int index);

Access substitute(Parameterization parTypeDecl);

Access createQualifiedAccess();

void transformation();

  /**
   * @attribute syn
   * @aspect Generics
   * @declaredat /Users/eric/Documents/workspaces/clara-soot/JastAddJ/Java1.5Frontend/Generics.jrag:244
   */
  @SuppressWarnings({"unchecked", "cast"})
  boolean isParameterizedType();
  /**
   * @attribute syn
   * @aspect Generics
   * @declaredat /Users/eric/Documents/workspaces/clara-soot/JastAddJ/Java1.5Frontend/Generics.jrag:245
   */
  @SuppressWarnings({"unchecked", "cast"})
  boolean isRawType();
  /**
   * @attribute syn
   * @aspect GenericsTypeCheck
   * @declaredat /Users/eric/Documents/workspaces/clara-soot/JastAddJ/Java1.5Frontend/Generics.jrag:380
   */
  @SuppressWarnings({"unchecked", "cast"})
  boolean sameArgument(ParTypeDecl decl);
  /**
   * @attribute syn
   * @aspect LookupParTypeDecl
   * @declaredat /Users/eric/Documents/workspaces/clara-soot/JastAddJ/Java1.5Frontend/Generics.jrag:577
   */
  @SuppressWarnings({"unchecked", "cast"})
  boolean sameSignature(Access a);
  /**
   * @attribute syn
   * @aspect LookupParTypeDecl
   * @declaredat /Users/eric/Documents/workspaces/clara-soot/JastAddJ/Java1.5Frontend/Generics.jrag:612
   */
  @SuppressWarnings({"unchecked", "cast"})
  boolean sameSignature(ArrayList list);
  /**
   * @attribute syn
   * @aspect GenericsParTypeDecl
   * @declaredat /Users/eric/Documents/workspaces/clara-soot/JastAddJ/Java1.5Frontend/GenericsParTypeDecl.jrag:30
   */
  @SuppressWarnings({"unchecked", "cast"})
  String nameWithArgs();
  /**
   * @attribute inh
   * @aspect GenericsParTypeDecl
   * @declaredat /Users/eric/Documents/workspaces/clara-soot/JastAddJ/Java1.5Frontend/GenericsParTypeDecl.jrag:45
   */
  TypeDecl genericDecl();
}
