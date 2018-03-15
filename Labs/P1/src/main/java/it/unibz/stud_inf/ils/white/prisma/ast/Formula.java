package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.Groundable;
import it.unibz.stud_inf.ils.white.prisma.Substitution;

import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

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
		return new MultaryConnectiveExpression(
			MultaryConnectiveExpression.Connective.AND,
			expressions.stream().map(e -> e.ground(substitution)).collect(Collectors.toList())
		);
	}

	public Set<Atom> model() {
		return ground().initialize().model();
	}

	public List<Set<Atom>> models(long n) {
		return ground().initialize().models(n);
	}
}
