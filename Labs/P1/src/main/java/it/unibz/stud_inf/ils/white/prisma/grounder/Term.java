package it.unibz.stud_inf.ils.white.prisma.grounder;

public abstract class Term {
	public abstract boolean isGround();
	public abstract Term substitute(Substitution substitution);
}
