package it.unibz.stud_inf.ils.white.prisma.grounder.parser;

import it.unibz.stud_inf.ils.white.prisma.grounder.IntExpression;

public class IntNumberExpression extends IntExpression {
	private final int number;

	public IntNumberExpression(int number) {
		this.number = number;
	}

	@Override
	public int toInteger() {
		return number;
	}
}
