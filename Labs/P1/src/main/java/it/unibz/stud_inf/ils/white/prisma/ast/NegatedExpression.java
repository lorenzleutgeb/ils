package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.CNF;
import it.unibz.stud_inf.ils.white.prisma.Substitution;

public class NegatedExpression extends Expression {
	private final Expression subExpression;

	public NegatedExpression(Expression subExpression) {
		this.subExpression = subExpression;
	}

	@Override
	public String toString() {
		return "~" + subExpression;
	}

	@Override
	public Expression ground(Substitution substitution) {
		if (subExpression instanceof NegatedExpression) {
			return ((NegatedExpression)subExpression).subExpression.ground(substitution);
		}
		if (subExpression instanceof Atom) {
			return new NegatedExpression(subExpression.ground(substitution));
		}
		return subExpression.ground(substitution).deMorgan();
	}

	@Override
	public boolean equals(Object o) {
		if (this == o) return true;
		if (o == null || getClass() != o.getClass()) return false;

		NegatedExpression that = (NegatedExpression) o;

		return subExpression.equals(that.subExpression);
	}

	@Override
	public int hashCode() {
		return subExpression.hashCode();
	}

	@Override
	public Integer normalize(CNF cnf) {
		if (!(subExpression instanceof Atom)) {
			throw new IllegalStateException("Formula must be in negation normal form.");
		}

		return -cnf.computeIfAbsent(subExpression);
	}

	@Override
	public Expression deMorgan() {
		return subExpression;
	}
}
