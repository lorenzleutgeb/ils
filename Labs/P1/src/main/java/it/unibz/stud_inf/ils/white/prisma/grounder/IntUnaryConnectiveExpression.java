package it.unibz.stud_inf.ils.white.prisma.grounder;

import static java.lang.Math.abs;

public class IntUnaryConnectiveExpression extends IntExpression {
	private final IntUnaryConnectiveExpression.Connective connective;
	private final IntExpression subExpression;

	public IntUnaryConnectiveExpression(Connective connective, IntExpression subExpression) {
		this.connective = connective;
		this.subExpression = subExpression;
	}

	public enum Connective {
		ABS("|"),
		NEG("-");

		private final String asString;

		Connective(String asString) {
			this.asString = asString;
		}

		@Override
		public String toString() {
			return asString;
		}
	}

	@Override
	public IntExpression substitute(Substitution substitution) {
		if (isGround()) {
			return this;
		}
		return new IntUnaryConnectiveExpression(
			connective,
			subExpression.substitute(substitution)
		);
	}

	@Override
	public boolean isGround() {
		return subExpression.isGround();
	}

	@Override
	public int toInteger() {
		int x = subExpression.toInteger();
		switch (connective) {
			case ABS:
				return abs(x);
			case NEG:
				return -x;
		}
		throw new UnsupportedOperationException();
	}
}
