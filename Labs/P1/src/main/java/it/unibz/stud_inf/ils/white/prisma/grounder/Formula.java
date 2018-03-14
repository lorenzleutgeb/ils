package it.unibz.stud_inf.ils.white.prisma.grounder;

import java.util.Iterator;
import java.util.List;
import java.util.stream.Collectors;

import static it.unibz.stud_inf.ils.white.prisma.grounder.BinaryConnectiveExpression.Connective.AND;
import static it.unibz.stud_inf.ils.white.prisma.grounder.BinaryConnectiveExpression.Connective.OR;
import static it.unibz.stud_inf.ils.white.prisma.grounder.Quantifier.FORALL;
import static java.util.Collections.emptyList;

public class Formula implements Iterable<Expression>, Groundable<Expression> {
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
		Expression acc = new Atom(ConstantPredicate.TRUE, emptyList());

		for (Expression e : expressions) {
			acc = new BinaryConnectiveExpression(
				AND,
				acc,
				e.ground(substitution)
			);
		}

		return acc;
	}

	public Expression ground() {
		return ground(new Substitution());
	}

	public Expression get(int i) {
		return expressions.get(i);
	}
}
