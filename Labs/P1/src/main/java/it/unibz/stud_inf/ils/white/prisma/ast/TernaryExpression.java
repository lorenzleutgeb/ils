package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.CNF;
import it.unibz.stud_inf.ils.white.prisma.Substitution;

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
		return "(" + condition + " ? " + truthy + " : " + falsy + ")";
	}

	@Override
	public Expression ground(Substitution substitution) {
		Expression condition = this.condition.ground(substitution);
		Expression truthy = this.truthy.ground(substitution);
		Expression falsy = this.falsy.ground(substitution);

		return new MultaryConnectiveExpression(
			MultaryConnectiveExpression.Connective.AND,
			new MultaryConnectiveExpression(
				MultaryConnectiveExpression.Connective.OR,
				new NegatedExpression(condition),
				truthy
			),
			new MultaryConnectiveExpression(
				MultaryConnectiveExpression.Connective.OR,
				condition,
				falsy
			)
		);
	}

	@Override
	public Integer normalize(CNF cnf) {
		throw new IllegalStateException();
	}

	@Override
	public Expression deMorgan() {
		throw new UnsupportedOperationException();
	}
}
