package it.unibz.stud_inf.ils.white.prisma.grounder;

public class QuantifiedExpression extends Expression {
	private final Quantifier quantifier;
	private final Variable variable;
	private final Domain domain;
	private final Expression subExpression;

	public QuantifiedExpression(Quantifier quantifier, Variable variable, Domain domain, Expression subExpression) {
		this.quantifier = quantifier;
		this.variable = variable;
		this.domain = domain;
		this.subExpression = subExpression;
	}

	@Override
	public String toString() {
		return quantifier.toString().toLowerCase() + " " + variable + " in " + domain + " " + subExpression;
	}
}
