package it.unibz.stud_inf.ils.white.prisma.ast.terms;

import it.unibz.stud_inf.ils.white.prisma.ast.Domain;
import it.unibz.stud_inf.ils.white.prisma.ast.Substitution;
import it.unibz.stud_inf.ils.white.prisma.ast.Variable;
import it.unibz.stud_inf.ils.white.prisma.util.Counter;

import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.stream.IntStream;
import java.util.stream.Stream;

public class IntExpressionRange extends Domain<IntNumberExpression> {
	private final IntExpression min;
	private final IntExpression max;

	public IntExpressionRange(IntExpression min, IntExpression max) {
		this.min = min;
		this.max = max;
	}

	@Override
	public Stream<IntNumberExpression> stream(Substitution substitution) {
		return IntStream.rangeClosed(
			min.ground(substitution).toInteger(),
			max.ground(substitution).toInteger()
		).mapToObj(IntNumberExpression::new);
	}

	@Override
	public Set<Variable> getOccurringVariables() {
		Set<Variable> result = new HashSet<>(min.getOccurringVariables().size() + max.getOccurringVariables().size());
		result.addAll(min.getOccurringVariables());
		result.addAll(max.getOccurringVariables());
		return result;
	}

	@Override
	public String toString() {
		return "[" + min + "…" + max + "]";
	}

	@Override
	public Domain<IntNumberExpression> standardize(Map<Variable, Variable> map, Counter generator) {
		return new IntExpressionRange(
			min.standardize(map, generator),
			max.standardize(map, generator)
		);
	}
}
