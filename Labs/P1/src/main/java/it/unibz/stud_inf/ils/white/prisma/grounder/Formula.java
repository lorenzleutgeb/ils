package it.unibz.stud_inf.ils.white.prisma.grounder;

import java.util.List;
import java.util.stream.Collectors;

public class Formula {
	private final List<Expression> expressions;

	public Formula(List<Expression> expressions) {
		this.expressions = expressions;
	}

	@Override
	public String toString() {
		return expressions.stream().map(Expression::toString).collect(Collectors.joining("\n"));
	}
}
