package it.unibz.stud_inf.ils.white.prisma.ast.terms;

import it.unibz.stud_inf.ils.white.prisma.ast.Substitution;
import it.unibz.stud_inf.ils.white.prisma.ast.Variable;
import it.unibz.stud_inf.ils.white.prisma.util.Counter;
import it.unibz.stud_inf.ils.white.prisma.util.Util;

import java.util.Collections;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

public class IntVariable extends IntExpression implements Variable<IntNumberExpression> {
	private final String raw;

	public IntVariable(String name) {
		this.raw = name;
	}

	@Override
	public IntNumberExpression ground(Substitution substitution) {
		return substitution.eval(this);
	}

	@Override
	public Set<Variable> getOccurringVariables() {
		return Collections.singleton(this);
	}

	@Override
	public String toString() {
		return "#" + raw;
	}

	@Override
	public boolean equals(Object o) {
		if (this == o) {
			return true;
		}
		if (o == null || getClass() != o.getClass()) {
			return false;
		}
		IntVariable that = (IntVariable) o;
		return Objects.equals(raw, that.raw);
	}

	@Override
	public int hashCode() {
		return Objects.hash(raw);
	}

	@Override
	public IntVariable standardize(Map<Variable, Variable> map, Counter generator) {
		return (IntVariable) map.get(this);
	}
}
