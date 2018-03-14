package it.unibz.stud_inf.ils.white.prisma.grounder;

import it.unibz.stud_inf.ils.white.prisma.grounder.Substitution;
import it.unibz.stud_inf.ils.white.prisma.grounder.Term;

public class ConstantTerm extends Term {
	private final String raw;

	public ConstantTerm(String raw) {
		this.raw = raw;
	}

	public boolean isGround() {
		return true;
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
