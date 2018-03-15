package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.Substitution;

import java.util.stream.Stream;

public abstract class Domain<T> {
	public abstract Stream<T> stream(Substitution substitution);

	public abstract int size();
}
