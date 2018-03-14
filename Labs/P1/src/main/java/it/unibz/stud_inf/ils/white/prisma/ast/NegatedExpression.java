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
		return new NegatedExpression(subExpression.ground(substitution));
	}

	public Expression getSubExpression() {
		return subExpression;
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
		Integer child = cnf.computeIfAbsent(getSubExpression());
		Integer self = cnf.put(this);

		cnf.add(self, child);
		cnf.add(-self, -child);

		return self;
	}
}
