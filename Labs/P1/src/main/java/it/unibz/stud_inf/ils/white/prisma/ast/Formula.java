package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.CNF;
import it.unibz.stud_inf.ils.white.prisma.Groundable;
import it.unibz.stud_inf.ils.white.prisma.IntIdGenerator;
import it.unibz.stud_inf.ils.white.prisma.Substitution;

import java.util.*;
import java.util.stream.Collectors;

public class Formula implements Iterable<Expression>, Groundable<Formula,Formula> {
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

	public Formula ground(Substitution substitution) {
		if (this.expressions.isEmpty()) {
			return new Formula(Collections.singletonList(Atom.TRUE));
		}

		List<Expression> expressions = this.standardize(new HashMap<>(), new IntIdGenerator()).expressions;

		if (expressions.size() == 1) {
			return new Formula(
				Collections.singletonList(expressions.get(0).ground(substitution))
			);
		}

		return new Formula(Collections.singletonList(new MultaryConnectiveExpression(
			MultaryConnectiveExpression.Connective.AND,
			expressions.stream().map(e -> e.ground(substitution)).collect(Collectors.toList())
		)));
	}

	public Formula normalize() {
		return new Formula(
			expressions.stream().map(Expression::normalize).collect(Collectors.toList())
		);
	}

	public CNF tseitin() {
		return expressions.get(0).tseitin();
	}

	public Formula standardize() {
		return standardize(new HashMap<>(), new IntIdGenerator());
	}

	public Formula prenex() {
		return new Formula(
			expressions.stream().map(Expression::prenex).collect(Collectors.toList())
		);
	}

	@Override
	public Formula standardize(Map<Long, Long> map, IntIdGenerator generator) {
		return new Formula(
			expressions.stream().map(e -> e.standardize(new HashMap<>(map), generator)).collect(Collectors.toList())
		);
	}
}
