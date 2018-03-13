package it.unibz.stud_inf.ils.white.prisma.grounder;

import java.util.Iterator;
import java.util.List;
import java.util.stream.Collectors;

public class PredicateDomain extends Domain<Predicate> {
	private final List<Predicate> predicates;
	private final boolean ground;

	public PredicateDomain(List<Predicate> predicates) {
		this.predicates = predicates;
		this.ground = predicates.stream().allMatch(p -> p instanceof ConstantPredicate);
	}

	@Override
	public Iterator<Predicate> iterator() {
		return predicates.iterator();
	}

	@Override
	public boolean isGround() {
		return this.ground;
	}

	@Override
	public Domain<Predicate> substitute(Substitution substitution) {
		if (this.ground) {
			return this;
		}
		return new PredicateDomain(
			predicates.stream().map(p -> p.substitute(substitution)).collect(Collectors.toList())
		);
	}
}
