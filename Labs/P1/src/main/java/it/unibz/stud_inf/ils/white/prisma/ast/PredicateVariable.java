package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.IntIdGenerator;
import it.unibz.stud_inf.ils.white.prisma.Substitution;

import java.util.Map;

public class PredicateVariable extends Predicate implements Variable<Predicate> {
	private final String raw;

	public PredicateVariable(String raw) {
		this.raw = raw;
	}

	@Override
	public Predicate ground(Substitution substitution) {
		return substitution.eval(this);
	}

	@Override
	public String toString() {
		return "@" + raw;
	}

	@Override
	public boolean equals(Object o) {
		if (this == o) return true;
		if (o == null || getClass() != o.getClass()) return false;

		PredicateVariable that = (PredicateVariable) o;

		return raw.equals(that.raw);
	}

	@Override
	public int hashCode() {
		return raw.hashCode();
	}

	@Override
	public Predicate standardize(Map<Variable, Integer> map, IntIdGenerator generator) {
		Integer id = map.get(this);
		if (id == null) {
			throw new RuntimeException("Free variable: "+ this);
		}
		return new PredicateVariable("v" + id);
	}
}
