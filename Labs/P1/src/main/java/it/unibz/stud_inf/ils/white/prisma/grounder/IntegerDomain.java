package it.unibz.stud_inf.ils.white.prisma.grounder;

import java.util.Iterator;
import java.util.stream.IntStream;

public class IntegerDomain extends Domain<Integer> {
	private final IntExpression min;
	private final IntExpression max;
	private final boolean ground;

	public IntegerDomain(IntExpression min, IntExpression max) {
		this.min = min;
		this.max = max;
		this.ground = min.isGround() && max.isGround();
	}

	@Override
	public Iterator<Integer> iterator() {
		return IntStream.rangeClosed(min.toInteger(), max.toInteger()).iterator();
	}

	@Override
	public boolean isGround() {
		return ground;
	}

	@Override
	public Domain<Integer> substitute(Substitution substitution) {
		if (isGround()) {
			return this;
		}
		return new IntegerDomain(
			min.substitute(substitution),
			max.substitute(substitution)
		);
	}
}
