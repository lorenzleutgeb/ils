package it.unibz.stud_inf.ils.white.prisma.grounder;

public class NegatedExpression extends Expression {
	private final Expression subExpression;

	public NegatedExpression(Expression subExpression) {
		this.subExpression = subExpression;
	}

	@Override
	public String toString() {
		return "~" + subExpression;
	}
}
