package it.unibz.stud_inf.ils.white.prisma.grounder;

import java.util.Iterator;
import java.util.stream.IntStream;

public class IntegerDomain extends Domain<Integer> {
	private final int lower;
	private final int upper;

	public IntegerDomain(int lower, int upper) {
		this.lower = lower;
		this.upper = upper;
	}

	@Override
	public Iterator<Integer> iterator() {
		return IntStream.rangeClosed(lower, upper).iterator();
	}
}
