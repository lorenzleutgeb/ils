package it.unibz.stud_inf.ils.white.prisma.grounder;

public abstract class Predicate {
	public abstract Predicate substitute(Substitution substitution);
}
