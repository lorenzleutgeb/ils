package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.CNF;
import it.unibz.stud_inf.ils.white.prisma.IntIdGenerator;
import it.unibz.stud_inf.ils.white.prisma.Standardizable;
import it.unibz.stud_inf.ils.white.prisma.Substitution;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import static it.unibz.stud_inf.ils.white.prisma.ast.MultaryConnectiveExpression.Connective.AND;
import static it.unibz.stud_inf.ils.white.prisma.ast.MultaryConnectiveExpression.Connective.OR;
import static it.unibz.stud_inf.ils.white.prisma.ast.Quantifier.FORALL;

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
		List<Expression> instances = new ArrayList<>(/*domain.size()*/);
		for (T instance : domain.stream(substitution).collect(Collectors.toList())) {
			substitution.put(variable, instance);
			instances.add(subExpression.ground(substitution));
		}

		return new MultaryConnectiveExpression(
			quantifier.equals(FORALL) ? AND : OR,
			instances
		);
	}

	@Override
	public QuantifiedExpression<T> standardize(Map<Variable, Integer> map, IntIdGenerator generator) {
		int id = generator.getNextId();
		Map<Variable, Integer> subMap = new HashMap<>(map);
		subMap.put(variable, id);
		Variable<T> variable = ((Variable<T>)((Standardizable)this.variable).standardize(subMap, generator));
		return new QuantifiedExpression<>(
			quantifier,
			variable,
			domain.standardize(subMap, generator),
			subExpression.standardize(subMap, generator)
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
