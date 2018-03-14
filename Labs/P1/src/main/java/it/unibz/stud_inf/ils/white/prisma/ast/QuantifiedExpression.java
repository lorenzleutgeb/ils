package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.CNF;
import it.unibz.stud_inf.ils.white.prisma.Substitution;

import java.util.stream.Collectors;

import static it.unibz.stud_inf.ils.white.prisma.ast.BinaryConnectiveExpression.Connective.AND;
import static it.unibz.stud_inf.ils.white.prisma.ast.BinaryConnectiveExpression.Connective.OR;
import static it.unibz.stud_inf.ils.white.prisma.ast.Quantifier.FORALL;
import static java.util.Collections.emptyList;

public class QuantifiedExpression<T> extends Expression {
	private final Quantifier quantifier;
	private final Variable<T> variable;
	private final Domain<T> domain;
	private final Expression subExpression;

	public QuantifiedExpression(Quantifier quantifier, Variable<T> variable, Domain<T> domain, Expression subExpression) {
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
	public Expression ground(Substitution substitution) {
		Expression acc = new Atom(quantifier.equals(FORALL) ? ConstantPredicate.TRUE : ConstantPredicate.FALSE, emptyList());

		for (T instance : domain.stream(substitution).collect(Collectors.toList())) {
			substitution.put(variable, instance);
			acc = new BinaryConnectiveExpression(
				quantifier.equals(FORALL) ? AND : OR,
				acc,
				subExpression.ground(substitution)
			);
		}

		return acc;
	}

	@Override
	public Integer normalize(CNF cnf) {
		throw new IllegalStateException();
	}
}
