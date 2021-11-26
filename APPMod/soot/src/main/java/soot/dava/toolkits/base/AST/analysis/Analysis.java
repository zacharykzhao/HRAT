package soot.dava.toolkits.base.AST.analysis;

/*-
 * #%L
 * Soot - a J*va Optimization Framework
 * %%
 * Copyright (C) 2005 Nomair A. Naeem
 * %%
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 2.1 of the
 * License, or (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Lesser Public License for more details.
 * 
 * You should have received a copy of the GNU General Lesser Public
 * License along with this program.  If not, see
 * <http://www.gnu.org/licenses/lgpl-2.1.html>.
 * #L%
 */

import soot.Type;
import soot.Value;
import soot.dava.internal.AST.ASTAndCondition;
import soot.dava.internal.AST.ASTBinaryCondition;
import soot.dava.internal.AST.ASTDoWhileNode;
import soot.dava.internal.AST.ASTForLoopNode;
import soot.dava.internal.AST.ASTIfElseNode;
import soot.dava.internal.AST.ASTIfNode;
import soot.dava.internal.AST.ASTLabeledBlockNode;
import soot.dava.internal.AST.ASTMethodNode;
import soot.dava.internal.AST.ASTOrCondition;
import soot.dava.internal.AST.ASTStatementSequenceNode;
import soot.dava.internal.AST.ASTSwitchNode;
import soot.dava.internal.AST.ASTSynchronizedBlockNode;
import soot.dava.internal.AST.ASTTryNode;
import soot.dava.internal.AST.ASTUnaryCondition;
import soot.dava.internal.AST.ASTUnconditionalLoopNode;
import soot.dava.internal.AST.ASTWhileNode;
import soot.dava.internal.javaRep.DVariableDeclarationStmt;
import soot.jimple.ArrayRef;
import soot.jimple.BinopExpr;
import soot.jimple.CastExpr;
import soot.jimple.DefinitionStmt;
import soot.jimple.Expr;
import soot.jimple.InstanceFieldRef;
import soot.jimple.InstanceInvokeExpr;
import soot.jimple.InstanceOfExpr;
import soot.jimple.InvokeExpr;
import soot.jimple.InvokeStmt;
import soot.jimple.NewArrayExpr;
import soot.jimple.NewMultiArrayExpr;
import soot.jimple.Ref;
import soot.jimple.ReturnStmt;
import soot.jimple.StaticFieldRef;
import soot.jimple.Stmt;
import soot.jimple.ThrowStmt;
import soot.jimple.UnopExpr;

public interface Analysis {

  void caseASTMethodNode(ASTMethodNode node);

  void caseASTSynchronizedBlockNode(ASTSynchronizedBlockNode node);

  void caseASTLabeledBlockNode(ASTLabeledBlockNode node);

  void caseASTUnconditionalLoopNode(ASTUnconditionalLoopNode node);

  void caseASTSwitchNode(ASTSwitchNode node);

  void caseASTIfNode(ASTIfNode node);

  void caseASTIfElseNode(ASTIfElseNode node);

  void caseASTWhileNode(ASTWhileNode node);

  void caseASTForLoopNode(ASTForLoopNode node);

  void caseASTDoWhileNode(ASTDoWhileNode node);

  void caseASTTryNode(ASTTryNode node);

  void caseASTStatementSequenceNode(ASTStatementSequenceNode node);

  void caseASTUnaryCondition(ASTUnaryCondition uc);

  void caseASTBinaryCondition(ASTBinaryCondition bc);

  void caseASTAndCondition(ASTAndCondition ac);

  void caseASTOrCondition(ASTOrCondition oc);

  void caseType(Type t);

  void caseDefinitionStmt(DefinitionStmt s);

  void caseReturnStmt(ReturnStmt s);

  void caseInvokeStmt(InvokeStmt s);

  void caseThrowStmt(ThrowStmt s);

  void caseDVariableDeclarationStmt(DVariableDeclarationStmt s);

  void caseStmt(Stmt s);

  void caseValue(Value v);

  void caseExpr(Expr e);

  void caseRef(Ref r);

  void caseBinopExpr(BinopExpr be);

  void caseUnopExpr(UnopExpr ue);

  void caseNewArrayExpr(NewArrayExpr nae);

  void caseNewMultiArrayExpr(NewMultiArrayExpr nmae);

  void caseInstanceOfExpr(InstanceOfExpr ioe);

  void caseInvokeExpr(InvokeExpr ie);

  void caseInstanceInvokeExpr(InstanceInvokeExpr iie);

  void caseCastExpr(CastExpr ce);

  void caseArrayRef(ArrayRef ar);

  void caseInstanceFieldRef(InstanceFieldRef ifr);

  void caseStaticFieldRef(StaticFieldRef sfr);
}
