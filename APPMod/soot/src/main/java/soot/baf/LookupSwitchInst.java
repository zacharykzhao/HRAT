package soot.baf;

/*-
 * #%L
 * Soot - a J*va Optimization Framework
 * %%
 * Copyright (C) 1999 Patrick Lam, Patrick Pominville and Raja Vallee-Rai
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

import java.util.List;

import soot.Unit;
import soot.UnitBox;
import soot.jimple.IntConstant;

public interface LookupSwitchInst extends Inst {
  Unit getDefaultTarget();

  void setDefaultTarget(Unit defTarget);

  UnitBox getDefaultTargetBox();

  void setLookupValue(int index, int value);

  int getLookupValue(int index);

  List<IntConstant> getLookupValues();

  void setLookupValues(List<IntConstant> values);

  int getTargetCount();

  Unit getTarget(int index);

  UnitBox getTargetBox(int index);

  void setTarget(int index, Unit target);

  List<Unit> getTargets();

  void setTargets(List<Unit> targets);
}
