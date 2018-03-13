package it.unibz.stud_inf.ils.white.prisma.grounder;

public class IntBinaryConnectiveExpression extends IntExpression {
	private final IntExpression left;
	private final Connective connective;
	private final IntExpression right;

	public enum Connective {
		MUL("*"),
		DIV("/"),
		MOD("%"),
		ADD("+"),
		SUB("-");

		private final String asString;

		Connective(String asString) {
			this.asString = asString;
		}

		public static IntBinaryConnectiveExpression.Connective fromOperator(String op) {
			for (IntBinaryConnectiveExpression.Connective c : IntBinaryConnectiveExpression.Connective.values()) {
				if (c.toString().equals(op)) {
					return c;
				}
			}
			return null;
		}

		@Override
		public String toString() {
			return asString;
		}
	}

	public IntBinaryConnectiveExpression(IntExpression left, Connective connective, IntExpression right) {
		this.left = left;
		this.connective = connective;
		this.right = right;
	}

	@Override
	public boolean isGround() {
		return left.isGround() && right.isGround();
	}

	@Override
	public IntExpression substitute(Substitution substitution) {
		if (isGround()) {
			return this;
		}

		return new IntBinaryConnectiveExpression(
			left.substitute(substitution),
			connective,
			right.substitute(substitution)
		);
	}

	@Override
	public int toInteger() {
		int left = this.left.toInteger();
		int right = this.right.toInteger();
		switch (connective) {
			case MUL:
				return left * right;
			case DIV:
				return left / right;
			case MOD:
				return left % right;
			case ADD:
				return left + right;
			case SUB:
				return left - right;
		}
		throw new UnsupportedOperationException();
	}
}
