package it.unibz.stud_inf.ils.white.prisma.grounder;

public abstract class Domain<T> implements Iterable<T> {
	//public abstract Stream<T> stream();

	public abstract boolean isGround();
	public abstract Domain<T> substitute(Substitution substitution);
}
