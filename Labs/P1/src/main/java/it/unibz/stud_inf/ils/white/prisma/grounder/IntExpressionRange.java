package it.unibz.stud_inf.ils.white.prisma.grounder;

import java.util.Iterator;
import java.util.stream.IntStream;
import java.util.stream.Stream;

public class IntExpressionRange extends Domain<IntNumberExpression> {
	private final IntExpression min;
	private final IntExpression max;

	public IntExpressionRange(IntExpression min, IntExpression max) {
		this.min = min;
		this.max = max;
	}

	public Stream<IntNumberExpression> stream(Substitution substitution) {
		return IntStream.rangeClosed(
			min.ground(substitution).toInteger(),
			max.ground(substitution).toInteger()
		).mapToObj(IntNumberExpression::new);
	}

	@Override
	public String toString() {
		return "[" + min + "..." + max + "]";
	}
}
