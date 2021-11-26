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
public interface Flags {

     
    int ACC_PUBLIC = 0x0001;

     
    int ACC_PRIVATE = 0x0002;

     
    int ACC_PROTECTED = 0x0004;

     
    int ACC_STATIC = 0x0008;

     
    int ACC_FINAL = 0x0010;

     
    int ACC_SUPER = 0x0020;

     
    int ACC_SYNCHRONIZED = 0x0020;

     
    int ACC_VOLATILE = 0x0040;

     
    int ACC_BRIDGE = 0x0040;

     
    int ACC_TRANSIENT = 0x0080;

     
    int ACC_VARARGS = 0x0080;

     
    int ACC_NATIVE = 0x0100;

     
    int ACC_INTERFACE = 0x0200;

     
    int ACC_ABSTRACT = 0x0400;

     
    int ACC_STRICT = 0x0800;

     
    int ACC_SYNTHETIC = 0x1000;

     
    int ACC_ANNOTATION = 0x2000;

     
    int ACC_ENUM = 0x4000;
}
