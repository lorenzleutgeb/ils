package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.Substitution;

public class IntVariable extends IntExpression implements Variable<IntNumberExpression> {
	private final String name;

	public IntVariable(String name) {
		this.name = name;
	}

	@Override
	public IntNumberExpression ground(Substitution substitution) {
		return substitution.eval(this);
	}

	@Override
	public String toString() {
		return "#" + name;
	}

	@Override
	public boolean equals(Object o) {
		if (this == o) return true;
		if (o == null || getClass() != o.getClass()) return false;

		IntVariable that = (IntVariable) o;

		return name.equals(that.name);
	}

	@Override
	public int hashCode() {
		return name.hashCode();
	}
}
