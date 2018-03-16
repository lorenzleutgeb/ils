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

public class QuantifiedExpression<T> extends Expression {
	private final Quantifier<T> quantifier;
	private final Expression scope;

	public Expression getScope() {
		return scope;
	}

	public QuantifiedExpression(Quantifier quantifier, Expression scope) {
		this.quantifier = quantifier;
		this.scope = scope;
	}

	public QuantifiedExpression<T> switchScope(Expression scope) {
		return new QuantifiedExpression<>(
			quantifier,
			scope
		);
	}

	@Override
	public String toString() {
		return quantifier.toString().toLowerCase() + " " + quantifier.getVariable() + " in " + quantifier.getDomain() + " " + scope;
	}

	@Override
	public Expression ground(Substitution substitution) {
		List<Expression> instances = new ArrayList<>(/*domain.size()*/);
		for (T instance : quantifier.getDomain().stream(substitution).collect(Collectors.toList())) {
			substitution.put(quantifier.getVariable(), instance);
			instances.add(scope.ground(substitution));
		}

		return new MultaryConnectiveExpression(
			quantifier.getConnective(),
			instances
		);
	}

	@Override
	public QuantifiedExpression<T> standardize(Map<Long, Long> map, IntIdGenerator generator) {
		long id = generator.getNextId();
		Map<Long, Long> subMap = new HashMap<>(map);
		subMap.put(quantifier.getVariable().toLong(), id);
		Variable<T> variable = ((Variable<T>)((Standardizable)quantifier.getVariable()).standardize(subMap, generator));
		return new QuantifiedExpression<T>(
			quantifier.switchBoth(
				variable,
				quantifier.getDomain().standardize(subMap, generator)
			),
			scope.standardize(subMap, generator)
		);
	}

	@Override
	public Expression prenex() {
		return switchScope(scope.prenex());
	}

	@Override
	public Integer tseitin(CNF cnf) {
		throw new IllegalStateException();
	}

	@Override
	public Expression deMorgan() {
		return new QuantifiedExpression<>(
			quantifier.flip(),
			scope.deMorgan()
		);
	}

	@Override
	public Expression normalize() {
		return switchScope(scope.normalize());
	}
}
