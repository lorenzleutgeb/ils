package it.unibz.stud_inf.ils.white.prisma.grounder.parser;

import it.unibz.stud_inf.ils.white.prisma.grounder.IntExpression;
import it.unibz.stud_inf.ils.white.prisma.grounder.Substitution;

public class IntNumberExpression extends IntExpression {
	private final int number;

	public IntNumberExpression(int number) {
		this.number = number;
	}

	@Override
	public IntExpression substitute(Substitution substitution) {
		return this;
	}

	@Override
	public boolean isGround() {
		return true;
	}

	@Override
	public int toInteger() {
		return number;
	}
}
