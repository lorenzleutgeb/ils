package it.unibz.stud_inf.ils.white.prisma.grounder;

import java.util.Collections;

public class QuantifiedExpression<T> extends Expression {
	private final Quantifier quantifier;
	private final Variable<T> variable;
	private final Domain<T> domain;
	private final Expression subExpression;

	public QuantifiedExpression(Quantifier quantifier, VariablePredicate variable, Domain<T> domain, Expression subExpression) {
		this.quantifier = quantifier;
		this.variable = variable;
		this.domain = domain;
		this.subExpression = subExpression;
	}

	@Override
	public String toString() {
		return quantifier.toString().toLowerCase() + " " + variable + " in " + domain + " " + subExpression;
	}

	@Override
	public Expression substitute(Substitution substitution) {
		return new QuantifiedExpression<>(
			quantifier,
			variable,
			domain.substitute(substitution),
			subExpression.substitute(substitution)
		);
	}

	@Override
	public Expression expand(Substitution substitution) {
		Expression acc = new Atom(quantifier.equals(Quantifier.FORALL) ? ConstantPredicate.TRUE : ConstantPredicate.FALSE, Collections.emptyList());

		for (T instance : domain.substitute(substitution)) {
			Substitution clone = new Substitution(substitution);
			clone.put(variable, instance);
			acc = new BinaryConnectiveExpression(
				quantifier.equals(Quantifier.FORALL) ? BinaryConnectiveExpression.Connective.AND : BinaryConnectiveExpression.Connective.OR,
				acc,
				subExpression.expand(clone)
			);
		}

		return acc;
	}
}
