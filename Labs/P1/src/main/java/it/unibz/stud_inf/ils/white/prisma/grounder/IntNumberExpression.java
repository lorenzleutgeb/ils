package it.unibz.stud_inf.ils.white.prisma.grounder;

import it.unibz.stud_inf.ils.white.prisma.grounder.IntExpression;
import it.unibz.stud_inf.ils.white.prisma.grounder.Substitution;

public class IntNumberExpression extends IntExpression {
	private final int number;

	public IntNumberExpression(int number) {
		this.number = number;
	}

	@Override
	public IntNumberExpression ground(Substitution substitution) {
		return this;
	}

	public boolean isGround() {
		return true;
	}

	public int toInteger() {
		return number;
	}

	@Override
	public String toString() {
		return String.valueOf(number);
	}
}
