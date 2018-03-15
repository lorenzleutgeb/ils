package it.unibz.stud_inf.ils.white.prisma.ast;

public enum Quantifier {
	EXISTS, FORALL;

	public Quantifier flip() {
		return this == EXISTS ? FORALL : EXISTS;
	}
}
