package it.unibz.stud_inf.ils.white.prisma.grounder;

public class VariablePredicate extends Predicate {
	private final String raw;

	public VariablePredicate(String raw) {
		this.raw = raw;
	}

	@Override
	public Predicate substitute(Substitution substitution) {
		return substitution.eval(this);
	}

	@Override
	public String toString() {
		return "_" + raw;
	}
}
