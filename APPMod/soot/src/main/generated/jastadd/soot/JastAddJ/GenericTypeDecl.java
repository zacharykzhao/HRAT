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
public interface GenericTypeDecl {

     
    TypeDecl original();

     
    int getNumTypeParameter();

     
    TypeVariable getTypeParameter(int index);

     
    List getTypeParameterList();

     
    String fullName();

     
    String typeName();
TypeDecl makeGeneric(Signatures.ClassSignature s);

SimpleSet addTypeVariables(SimpleSet c, String name);

List createArgumentList(ArrayList params);

  /**
   * @attribute syn
   * @aspect Generics
   * @declaredat /Users/eric/Documents/workspaces/clara-soot/JastAddJ/Java1.5Frontend/Generics.jrag:158
   */
  @SuppressWarnings({"unchecked", "cast"})
  boolean isGenericType();
  /**
   * @attribute syn
   * @aspect Generics
   * @declaredat /Users/eric/Documents/workspaces/clara-soot/JastAddJ/Java1.5Frontend/Generics.jrag:163
   */
  @SuppressWarnings({"unchecked", "cast"})
  TypeDecl rawType();
  /**
   * @attribute syn
   * @aspect LookupParTypeDecl
   * @declaredat /Users/eric/Documents/workspaces/clara-soot/JastAddJ/Java1.5Frontend/Generics.jrag:708
   */
  @SuppressWarnings({"unchecked", "cast"})
  TypeDecl lookupParTypeDecl(ParTypeAccess p);
  /**
   * @attribute syn
   * @aspect LookupParTypeDecl
   * @declaredat /Users/eric/Documents/workspaces/clara-soot/JastAddJ/Java1.5Frontend/Generics.jrag:714
   */
  @SuppressWarnings({"unchecked", "cast"})
  TypeDecl lookupParTypeDecl(ArrayList list);
}
