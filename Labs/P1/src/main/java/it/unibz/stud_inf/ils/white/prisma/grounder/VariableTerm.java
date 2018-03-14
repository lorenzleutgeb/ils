package it.unibz.stud_inf.ils.white.prisma.grounder;

import it.unibz.stud_inf.ils.white.prisma.grounder.Substitution;
import it.unibz.stud_inf.ils.white.prisma.grounder.Term;
import it.unibz.stud_inf.ils.white.prisma.grounder.Variable;

public class VariableTerm extends Term implements Variable<ConstantTerm> {
	private final String raw;

	public VariableTerm(String raw) {
		this.raw = raw;
	}

	public boolean isGround() {
		return false;
	}

	@Override
	public ConstantTerm ground(Substitution substitution) {
		return substitution.eval(this);
	}

	@Override
	public String toString() {
		return "$" + raw;
	}

	@Override
	public boolean equals(Object o) {
		if (this == o) return true;
		if (o == null || getClass() != o.getClass()) return false;

		VariableTerm that = (VariableTerm) o;

		return raw.equals(that.raw);
	}

	@Override
	public int hashCode() {
		return raw.hashCode();
	}
}
