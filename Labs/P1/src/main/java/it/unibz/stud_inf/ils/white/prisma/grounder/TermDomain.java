package it.unibz.stud_inf.ils.white.prisma.grounder;

import java.util.Iterator;
import java.util.List;

public class TermDomain extends Domain<Term> {
	private final List<Term> terms;

	public TermDomain(List<Term> terms) {
		this.terms = terms;
	}

	@Override
	public Iterator iterator() {
		return terms.iterator();
	}
}
