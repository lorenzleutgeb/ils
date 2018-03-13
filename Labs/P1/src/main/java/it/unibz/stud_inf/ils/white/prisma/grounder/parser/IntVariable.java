package it.unibz.stud_inf.ils.white.prisma.grounder.parser;

import it.unibz.stud_inf.ils.white.prisma.grounder.IntExpression;
import it.unibz.stud_inf.ils.white.prisma.grounder.Substitution;

public class IntVariable extends IntExpression {
	private final String name;

	public IntVariable(String name) {
		this.name = name;
	}

	@Override
	public IntExpression substitute(Substitution substitution) {
		return substitution.eval(this);
	}

	@Override
	public boolean isGround() {
		return false;
	}

	@Override
	public int toInteger() {
		throw new UnsupportedOperationException("Not yet implemented.");
	}
}
