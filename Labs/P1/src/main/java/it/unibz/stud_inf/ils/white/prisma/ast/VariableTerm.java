package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.Substitution;

public class VariableTerm extends Term implements Variable<ConstantTerm> {
	private final String raw;

	public VariableTerm(String raw) {
		this.raw = raw;
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
