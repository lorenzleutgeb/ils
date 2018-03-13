package it.unibz.stud_inf.ils.white.prisma.grounder.parser;

import it.unibz.stud_inf.ils.white.prisma.grounder.Term;

public class ConstantTerm extends Term {
	private final String raw;

	public ConstantTerm(String raw) {
		this.raw = raw;
	}

	@Override
	public boolean isGround() {
		return true;
	}
}
