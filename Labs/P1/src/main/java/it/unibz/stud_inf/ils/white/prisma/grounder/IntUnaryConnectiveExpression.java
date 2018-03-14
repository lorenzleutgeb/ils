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
	public IntNumberExpression ground(Substitution substitution) {
		int x = subExpression.ground(substitution).toInteger();

		switch (connective) {
			case ABS:
				x = abs(x);
			case NEG:
				x = -x;
		}

		return new IntNumberExpression(x);
	}
}
