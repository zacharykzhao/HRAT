package soot.grimp;

/*-
 * #%L
 * Soot - a J*va Optimization Framework
 * %%
 * Copyright (C) 1999 Patrick Lam
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

import soot.jimple.AddExpr;
import soot.jimple.AndExpr;
import soot.jimple.CastExpr;
import soot.jimple.CmpExpr;
import soot.jimple.CmpgExpr;
import soot.jimple.CmplExpr;
import soot.jimple.DivExpr;
import soot.jimple.EqExpr;
import soot.jimple.ExprSwitch;
import soot.jimple.GeExpr;
import soot.jimple.GtExpr;
import soot.jimple.InstanceOfExpr;
import soot.jimple.InterfaceInvokeExpr;
import soot.jimple.LeExpr;
import soot.jimple.LengthExpr;
import soot.jimple.LtExpr;
import soot.jimple.MulExpr;
import soot.jimple.NeExpr;
import soot.jimple.NegExpr;
import soot.jimple.NewArrayExpr;
import soot.jimple.NewExpr;
import soot.jimple.NewMultiArrayExpr;
import soot.jimple.OrExpr;
import soot.jimple.RemExpr;
import soot.jimple.ShlExpr;
import soot.jimple.ShrExpr;
import soot.jimple.SpecialInvokeExpr;
import soot.jimple.StaticInvokeExpr;
import soot.jimple.SubExpr;
import soot.jimple.UshrExpr;
import soot.jimple.VirtualInvokeExpr;
import soot.jimple.XorExpr;

public interface GrimpExprSwitch extends ExprSwitch {
  void caseAddExpr(AddExpr v);

  void caseAndExpr(AndExpr v);

  void caseCmpExpr(CmpExpr v);

  void caseCmpgExpr(CmpgExpr v);

  void caseCmplExpr(CmplExpr v);

  void caseDivExpr(DivExpr v);

  void caseEqExpr(EqExpr v);

  void caseNeExpr(NeExpr v);

  void caseGeExpr(GeExpr v);

  void caseGtExpr(GtExpr v);

  void caseLeExpr(LeExpr v);

  void caseLtExpr(LtExpr v);

  void caseMulExpr(MulExpr v);

  void caseOrExpr(OrExpr v);

  void caseRemExpr(RemExpr v);

  void caseShlExpr(ShlExpr v);

  void caseShrExpr(ShrExpr v);

  void caseUshrExpr(UshrExpr v);

  void caseSubExpr(SubExpr v);

  void caseXorExpr(XorExpr v);

  void caseInterfaceInvokeExpr(InterfaceInvokeExpr v);

  void caseSpecialInvokeExpr(SpecialInvokeExpr v);

  void caseStaticInvokeExpr(StaticInvokeExpr v);

  void caseVirtualInvokeExpr(VirtualInvokeExpr v);

  void caseNewInvokeExpr(NewInvokeExpr v);

  void caseCastExpr(CastExpr v);

  void caseInstanceOfExpr(InstanceOfExpr v);

  void caseNewArrayExpr(NewArrayExpr v);

  void caseNewMultiArrayExpr(NewMultiArrayExpr v);

  void caseNewExpr(NewExpr v);

  void caseLengthExpr(LengthExpr v);

  void caseNegExpr(NegExpr v);

  void defaultCase(Object obj);
}
