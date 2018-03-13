package it.unibz.stud_inf.ils.white.prisma.grounder;

public abstract class Expression {
	public abstract Expression substitute(Substitution substitution);

	public Expression expand(Substitution substitution) {
		return this;
	}
}
