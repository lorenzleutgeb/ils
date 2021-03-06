package it.unibz.stud_inf.ils.white.prisma.ast.expressions;

import it.unibz.stud_inf.ils.white.prisma.ast.Substitution;
import it.unibz.stud_inf.ils.white.prisma.ast.Variable;
import it.unibz.stud_inf.ils.white.prisma.ast.terms.IntExpression;
import it.unibz.stud_inf.ils.white.prisma.ast.terms.IntNumberExpression;
import it.unibz.stud_inf.ils.white.prisma.util.Counter;

import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class IntBinaryConnectiveExpression extends IntExpression {
	private final IntExpression left;
	private final Connective connective;
	private final IntExpression right;

	@Override
	public IntExpression standardize(Map<Variable, Variable> map, Counter generator) {
		return new IntBinaryConnectiveExpression(
			left.standardize(map, generator),
			connective,
			right.standardize(map, generator)
		);
	}

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
		if (left == null || connective == null || right == null) {
			throw new NullPointerException();
		}

		this.left = left;
		this.connective = connective;
		this.right = right;
	}

	@Override
	public IntNumberExpression ground(Substitution substitution) {
		int left = this.left.ground(substitution).toInteger();
		int right = this.right.ground(substitution).toInteger();

		switch (connective) {
			case MUL:
				return new IntNumberExpression(left * right);
			case DIV:
				return new IntNumberExpression(left / right);
			case MOD:
				return new IntNumberExpression(left % right);
			case ADD:
				return new IntNumberExpression(left + right);
			case SUB:
				return new IntNumberExpression(left - right);
			default:
				throw new UnsupportedOperationException();
		}
	}

	@Override
	public Set<Variable> getOccurringVariables() {
		Set<Variable> result = new HashSet<>(left.getOccurringVariables().size() + right.getOccurringVariables().size());
		result.addAll(left.getOccurringVariables());
		result.addAll(right.getOccurringVariables());
		return result;
	}

	@Override
	public String toString() {
		return left + " " + connective + " " + right;
	}
}
