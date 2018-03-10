package it.unibz.stud_inf.ils.white.prisma.grounder;

public class BinaryConnectiveExpression extends Expression {
	public BinaryConnectiveExpression(Connective connective, Expression left, Expression right) {
		this.connective = connective;
		this.left = left;
		this.right = right;
	}

	@Override
	public String toString() {
		return left + " " + connective + " " + right;
	}

	public enum Connective {
		THEN("=>"),
		IFF("<=>"),
		IF("<="),
		AND("&"),
		OR("|"),
		XOR("^");

		private final String asString;

		Connective(String asString) {
			this.asString = asString;
		}

		@Override
		public String toString() {
			return asString;
		}
	}

	private final Connective connective;
	private final Expression left;
	private final Expression right;
}
