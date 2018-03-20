package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.IntIdGenerator;
import it.unibz.stud_inf.ils.white.prisma.Substitution;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
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
			substitution.remove(quantifier.getVariable());
		}

		return new MultaryConnectiveExpression(
			quantifier.getConnective(),
			instances
		).compress();
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
	public Expression pushQuantifiersDown() {
		if (scope instanceof QuantifiedExpression) {
			// Check whether we should "jump".
			// Three conditions must be satisfied:
			//  1. Variables are not related.
			//  2. Domains are not dependent.
			//  3. this is quantified existentially.

			if (quantifier.isUniversal()) {
				return switchScope(scope.pushQuantifiersDown());
			}

			final var scope = (QuantifiedExpression) this.scope;

			if (quantifier.isExististential() && scope.quantifier.isExististential()) {
				return switchScope(scope.pushQuantifiersDown());
			}

			if (scope.scope.getRelatedVariables().stream().anyMatch(
				s -> s.contains(this.quantifier.getVariable()) && s.contains(scope.quantifier.getVariable())
			)) {
				return switchScope(scope.pushQuantifiersDown());
			}

			if (scope.quantifier.getDomain().getOccurringVariables().contains(quantifier.getVariable())) {
				return switchScope(scope.pushQuantifiersDown());
			}

			return scope.switchScope(
				switchScope(scope.scope)
			).pushQuantifiersDown();
		}
		if ((scope instanceof NegatedExpression) || (scope instanceof Atom)) {
			return switchScope(scope.pushQuantifiersDown());
		}
		if (!(scope instanceof MultaryConnectiveExpression)) {
			throw new IllegalStateException();
		}

		MultaryConnectiveExpression connectiveExpression = (MultaryConnectiveExpression) this.scope;

		if (connectiveExpression.isClause()) {
			return this;
		}

		Expression l = connectiveExpression.getLeft();
		Expression r = connectiveExpression.getRight();

		boolean cl = l.getOccurringVariables().contains(quantifier.getVariable());
		boolean cr = r.getOccurringVariables().contains(quantifier.getVariable());

		if (cl == cr) {
			if (!cr) {
				// Remove useless quantifier.
				return this.scope;
			} else {
				return this;
			}
		}

		Expression shouldBeScope = cr ? r : l;
		Expression other = cr ? l : r;


		return connectiveExpression.swap(
			switchScope(shouldBeScope.pushQuantifiersDown()),
			other.pushQuantifiersDown()
		);
	}

	@Override
	public Integer tseitin(it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm cnf) {
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

	@Override
	public Set<Variable> getOccurringVariables() {
		Set<Variable> sub = new HashSet<>(scope.getOccurringVariables());
		sub.remove(quantifier.getVariable());
		return sub;
	}

	@Override
	public Set<Set<Variable>> getRelatedVariables() {
		return scope.getRelatedVariables();
	}
}
