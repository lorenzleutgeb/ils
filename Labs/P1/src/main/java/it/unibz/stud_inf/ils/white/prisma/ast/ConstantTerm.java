package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.Substitution;

public class ConstantTerm extends Term {
	private final String raw;

	public ConstantTerm(String raw) {
		this.raw = raw;
	}

	@Override
	public ConstantTerm ground(Substitution substitution) {
		return this;
	}

	@Override
	public String toString() {
		return raw;
	}
}
