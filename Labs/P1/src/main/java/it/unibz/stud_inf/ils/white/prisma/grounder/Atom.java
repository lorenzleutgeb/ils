package it.unibz.stud_inf.ils.white.prisma.grounder;

import java.util.List;
import java.util.stream.Collectors;

public class Atom extends Expression {
	private final Predicate predicate;
	private final List<Term> terms;
	private final boolean ground;

	public Atom(Predicate predicate, List<Term> terms) {
		this.predicate = predicate;
		this.terms = terms;
		this.ground = (predicate instanceof ConstantPredicate) && terms.stream().allMatch(Term::isGround);
	}

	@Override
	public Expression substitute(Substitution substitution) {
		if (this.ground) {
			return this;
		}

		return new Atom(
			predicate.substitute(substitution),
			terms.stream().map(t -> t.substitute(substitution)).collect(Collectors.toList())
		);
	}

	public boolean isGround() {
		return ground;
	}
}
