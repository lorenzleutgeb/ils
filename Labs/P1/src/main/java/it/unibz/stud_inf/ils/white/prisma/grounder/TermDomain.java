package it.unibz.stud_inf.ils.white.prisma.grounder;

import it.unibz.stud_inf.ils.white.prisma.grounder.parser.ConstantTerm;

import java.util.Iterator;
import java.util.List;
import java.util.stream.Collectors;

public class TermDomain extends Domain<Term> {
	private final List<Term> terms;
	private final boolean ground;

	public TermDomain(List<Term> terms) {
		this.terms = terms;
		this.ground = terms.stream().allMatch(p -> p instanceof ConstantTerm);
	}

	@Override
	public Iterator<Term> iterator() {
		return terms.iterator();
	}

	@Override
	public boolean isGround() {
		return this.ground;
	}

	@Override
	public Domain<Term> substitute(Substitution substitution) {
		if (this.ground) {
			return this;
		}
		return new TermDomain(
			terms.stream().map(p -> p.substitute(substitution)).collect(Collectors.toList())
		);
	}
}
