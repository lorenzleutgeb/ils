package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.CNF;
import it.unibz.stud_inf.ils.white.prisma.Groundable;
import it.unibz.stud_inf.ils.white.prisma.IntIdGenerator;
import it.unibz.stud_inf.ils.white.prisma.Substitution;

import java.util.*;
import java.util.stream.Collectors;

public class Formula implements Iterable<Expression>, Groundable<Expression,Formula> {
	private final List<Expression> expressions;

	public Formula(List<Expression> expressions) {
		this.expressions = expressions;
	}

	@Override
	public String toString() {
		return expressions.stream().map(Expression::toString).collect(Collectors.joining("\n"));
	}

	@Override
	public Iterator<Expression> iterator() {
		return expressions.iterator();
	}

	public Expression ground(Substitution substitution) {
		if (this.expressions.isEmpty()) {
			return Atom.TRUE;
		}

		List<Expression> expressions = this.standardize(new HashMap<>(), new IntIdGenerator()).expressions;

		if (expressions.size() == 1) {
			return expressions.get(0).ground(substitution);
		}

		return new MultaryConnectiveExpression(
			MultaryConnectiveExpression.Connective.AND,
			expressions.stream().map(e -> e.ground(substitution)).collect(Collectors.toList())
		);
	}

	public CNF normalize() {
		return ground().normalize();
	}

	@Override
	public Formula standardize(Map<Variable, Integer> map, IntIdGenerator generator) {
		return new Formula(
			expressions.stream().map(e -> e.standardize(new HashMap<>(map), generator)).collect(Collectors.toList())
		);
	}
}
