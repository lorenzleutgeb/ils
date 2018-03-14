package it.unibz.stud_inf.ils.white.prisma.grounder;

import javassist.expr.Expr;

public class BinaryConnectiveExpression extends Expression {
	public BinaryConnectiveExpression(Connective connective, Expression left, Expression right) {
		this.connective = connective;
		this.left = left;
		this.right = right;
	}

	@Override
	public String toString() {
		return "(" + left + " " + connective + " " + right + ")";
	}

	@Override
	public Expression ground(Substitution substitution) {
		Expression left = this.left.ground(substitution);
		Expression right  = this.right.ground(substitution);

		switch (this.connective) {
			case THEN:
				return new BinaryConnectiveExpression(
					Connective.OR,
					new NegatedExpression(left),
					right
				);
			case IFF:
				return new BinaryConnectiveExpression(
					Connective.AND,
					new BinaryConnectiveExpression(
						Connective.OR,
						new NegatedExpression(left),
						right
					),
					new BinaryConnectiveExpression(
						Connective.OR,
						new NegatedExpression(right),
						left
					)
				);
			case IF:
				return new BinaryConnectiveExpression(
					Connective.OR,
					left,
					new NegatedExpression(right)
				);
			case XOR:
				return new BinaryConnectiveExpression(
					Connective.OR,
					new BinaryConnectiveExpression(
						Connective.AND,
						new NegatedExpression(left),
						right
					),
					new BinaryConnectiveExpression(
						Connective.AND,
						new NegatedExpression(right),
						left
					)
				);
		}

		return new BinaryConnectiveExpression(connective, left, right);
	}

	public Connective getConnective() {
		return connective;
	}

	public Expression getLeft() {
		return left;
	}

	public Expression getRight() {
		return right;
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

		public static Connective fromOperator(String op) {
			for (Connective c : Connective.values()) {
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

	private final Connective connective;
	private final Expression left;
	private final Expression right;

	@Override
	public boolean equals(Object o) {
		if (this == o) return true;
		if (o == null || getClass() != o.getClass()) return false;

		BinaryConnectiveExpression that = (BinaryConnectiveExpression) o;

		if (connective != that.connective) return false;
		if (!left.equals(that.left)) return false;
		return right.equals(that.right);
	}

	@Override
	public int hashCode() {
		int result = connective.hashCode();
		result = 31 * result + left.hashCode();
		result = 31 * result + right.hashCode();
		return result;
	}
}
