package it.unibz.stud_inf.ils.white.prisma.grounder;

public class TernaryExpression extends Expression {
	private final Expression condition;
	private final Expression truthy;
	private final Expression falsy;

	public TernaryExpression(Expression condition, Expression truthy, Expression falsy) {
		this.condition = condition;
		this.truthy = truthy;
		this.falsy = falsy;
	}

	@Override
	public String toString() {
		return condition + " ? " + truthy + " : " + falsy;
	}
}
