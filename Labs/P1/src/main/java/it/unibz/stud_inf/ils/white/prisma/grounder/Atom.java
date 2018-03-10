package it.unibz.stud_inf.ils.white.prisma.grounder;

import java.util.List;

public class Atom extends Expression {
	private final String predicate;
	private final List<Term> terms;

	public Atom(String predicate, List<Term> terms) {
		this.predicate = predicate;
		this.terms = terms;
	}
}
