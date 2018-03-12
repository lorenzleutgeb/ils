package it.unibz.stud_inf.ils.white.prisma.grounder.parser;

import it.unibz.stud_inf.ils.white.prisma.grounder.IntExpression;

public class IntVariable extends IntExpression {
	private final String name;

	public IntVariable(String name) {
		this.name = name;
	}

	@Override
	public int toInteger() {
		throw new UnsupportedOperationException("Not yet implemented.");
	}
}
