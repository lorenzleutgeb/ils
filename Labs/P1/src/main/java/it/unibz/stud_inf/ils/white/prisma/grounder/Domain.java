package it.unibz.stud_inf.ils.white.prisma.grounder;

import java.util.stream.Stream;

public abstract class Domain<T> {
	public abstract Stream<T> stream(Substitution substitution);
}
