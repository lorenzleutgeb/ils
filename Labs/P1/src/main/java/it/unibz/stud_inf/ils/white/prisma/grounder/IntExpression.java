package it.unibz.stud_inf.ils.white.prisma.grounder;

public abstract class IntExpression extends Term {
	public abstract IntExpression substitute(Substitution substitution);
	public abstract int toInteger();
}
