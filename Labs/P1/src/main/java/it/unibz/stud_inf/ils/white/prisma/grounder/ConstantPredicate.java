package it.unibz.stud_inf.ils.white.prisma.grounder;

public class ConstantPredicate extends Predicate {
	public static final ConstantPredicate TRUE = new ConstantPredicate("true");
	public static final ConstantPredicate FALSE = new ConstantPredicate("false");

	private final String raw;

	public ConstantPredicate(String raw) {
		this.raw = raw;
	}

	@Override
	public String toString() {
		return raw;
	}

	@Override
	public Predicate substitute(Substitution substitution) {
		return this;
	}
}
