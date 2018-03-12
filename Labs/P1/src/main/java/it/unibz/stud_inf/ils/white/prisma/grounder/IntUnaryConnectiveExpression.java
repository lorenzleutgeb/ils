package it.unibz.stud_inf.ils.white.prisma.grounder;

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
	public int toInteger() {
		int x = subExpression.toInteger();
		switch (connective) {
			case ABS:
				return Math.abs(x);
			case NEG:
				return -x;
		}
		throw new UnsupportedOperationException();
	}
}
