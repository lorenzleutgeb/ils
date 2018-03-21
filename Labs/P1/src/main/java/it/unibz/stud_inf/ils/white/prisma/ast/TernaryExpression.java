package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm;
import it.unibz.stud_inf.ils.white.prisma.IntIdGenerator;
import it.unibz.stud_inf.ils.white.prisma.Substitution;

import java.util.Map;

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
		return new TernaryExpression(
			condition.ground(substitution),
			truthy.ground(substitution),
			falsy.ground(substitution)
		);
	}

	@Override
	public Integer tseitin(ConjunctiveNormalForm cnf) {
		throw new IllegalStateException();
	}

	@Override
	public Expression normalize() {
		return and(
			or(not(condition).normalize(), truthy.normalize()),
			or(condition.normalize(), falsy.normalize())
		);
	}

	@Override
	public Expression standardize(Map<Long, Long> map, IntIdGenerator generator) {
		return new TernaryExpression(
			condition.standardize(map, generator),
			truthy.standardize(map, generator),
			falsy.standardize(map, generator)
		);
	}
}
