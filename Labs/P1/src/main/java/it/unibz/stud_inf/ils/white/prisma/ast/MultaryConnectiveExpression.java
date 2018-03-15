package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.CNF;
import it.unibz.stud_inf.ils.white.prisma.IntIdGenerator;
import it.unibz.stud_inf.ils.white.prisma.Substitution;

import java.util.*;
import java.util.stream.Collectors;

import static java.util.stream.Collectors.joining;

public class MultaryConnectiveExpression extends Expression {
	private final Connective connective;
	private final List<Expression> expressions;

	public MultaryConnectiveExpression(Connective connective, List<Expression> expressions) {
		if (expressions.stream().anyMatch(Objects::isNull)) {
			throw new NullPointerException();
		}
		if (expressions.stream().allMatch(e -> {
			return (e instanceof MultaryConnectiveExpression) && ((MultaryConnectiveExpression)e).connective.equals(connective);
		})) {
			this.expressions = expressions.stream().flatMap(e -> ((MultaryConnectiveExpression)e).expressions.stream()).collect(Collectors.toList());
		} else {
			this.expressions = expressions;
		}
		this.connective = connective;
	}

	public MultaryConnectiveExpression(Connective connective, Expression... expressions) {
		if (expressions.length != 2 && !(Connective.AND.equals(connective) || Connective.OR.equals(connective))) {
			throw new IllegalArgumentException("Refusing multary connective");
		}
		this.connective = connective;
		this.expressions = Arrays.asList(expressions);
		if (this.expressions.stream().anyMatch(Objects::isNull)) {
			throw new NullPointerException();
		}
	}

	@Override
	public String toString() {
		return expressions
			.stream()
			.map(Object::toString)
			.collect(joining(" " + connective + " ", "(", ")"));
	}

	@Override
	public Expression prenex() {
		if (expressions.size() != 2 && (Connective.AND.equals(connective) || Connective.OR.equals(connective))) {
			throw new UnsupportedOperationException();
		}

		Expression l = expressions.get(0).prenex();
		Expression r = expressions.get(1).prenex();

		boolean ql = l instanceof QuantifiedExpression;
		boolean qr = r instanceof QuantifiedExpression;

		if (qr == ql && !qr) {
			return new MultaryConnectiveExpression(
				connective,
				l,
				r
			);
		}

		if (qr == ql && qr) {
			QuantifiedExpression q1 = (QuantifiedExpression)l;
			QuantifiedExpression q2 = (QuantifiedExpression)r;
			return q1.switchScope(
				q2.switchScope(
					new MultaryConnectiveExpression(
						connective,
						q1.getScope(),
						q2.getScope()
					)
				)
			);
		}

		Expression e = qr ? l : r;
		QuantifiedExpression q = (QuantifiedExpression)(ql ? l : r);

		return q.switchScope(
			new MultaryConnectiveExpression(
				connective,
				e,
				q.getScope()
			)
		);
	}

	@Override
	public Expression normalize() {
		if (expressions.size() != 2) {
			throw new UnsupportedOperationException();
		}

		Expression left = expressions.get(0);
		Expression right = expressions.get(1);

		switch (this.connective) {
			case THEN:
				return new MultaryConnectiveExpression(
					Connective.OR,
					new NegatedExpression(left).normalize(),
					right.normalize()
				);
			case IFF:
				return new MultaryConnectiveExpression(
					Connective.AND,
					new MultaryConnectiveExpression(
						Connective.OR,
						new NegatedExpression(left).normalize(),
						right.normalize()
					),
					new MultaryConnectiveExpression(
						Connective.OR,
						new NegatedExpression(right).normalize(),
						left.normalize()
					)
				);
			case IF:
				return new MultaryConnectiveExpression(
					Connective.OR,
					left.normalize(),
					new NegatedExpression(right).normalize()
				);
			case XOR:
				return new MultaryConnectiveExpression(
					Connective.AND,
					new MultaryConnectiveExpression(
						Connective.OR,
						left,
						right
					).normalize(),
					new MultaryConnectiveExpression(
						Connective.OR,
						new NegatedExpression(right),
						new NegatedExpression(left)
					).normalize()
				);
		}

		return new MultaryConnectiveExpression(connective, left.normalize(), right.normalize());
	}

	@Override
	public Expression ground(Substitution substitution) {
		return new MultaryConnectiveExpression(
			connective,
			expressions.stream().map(e -> e.ground(substitution)).collect(Collectors.toList())
		);
	}

	@Override
	public Integer tseitin(CNF cnf) {
		if (!connective.equals(Connective.OR) && !connective.equals(Connective.AND)) {
			throw new IllegalStateException();
		}

		List<Integer> variables = expressions
			.stream()
			.map(cnf::computeIfAbsent)
			.collect(Collectors.toList());

		Integer self = cnf.put(this);

		int factor = Connective.AND.equals(connective) ? -1 : 1;

		// These three lines depend on the implementation of ArrayList.
		final int[] clause = new int[variables.size() + 1];
		for (int i = 0; i < variables.size(); i++) {
			clause[i] = variables.get(i) * factor;
		}
		clause[variables.size()] = -self * factor;
		cnf.add(clause);

		for (Integer variable : variables) {
			cnf.add(self * factor, -variable * factor);
		}

		return self;
	}

	@Override
	public Expression deMorgan() {
		return new MultaryConnectiveExpression(
			Connective.AND.equals(connective) ? Connective.OR : Connective.AND,
			expressions.stream().map(Expression::deMorgan).collect(Collectors.toList())
		);
	}

	public CNF tseitinFast() {
		if (Connective.OR.equals(connective)) {
			CNF cnf = new CNF();
			int[] cnfClause = new int[expressions.size()];
			for (int i = 0; i < expressions.size(); i++) {
				Expression it = expressions.get(i);
				if (it instanceof Atom) {
					int variable = cnf.shallowComputeIfAbsent(it);
					cnfClause[i] = variable;
				} else if (it instanceof NegatedExpression) {
					int variable = cnf.shallowComputeIfAbsent(((NegatedExpression) it).getAtom());
					cnfClause[i] = -variable;
				} else {
					return null;
				}
			}
			cnf.add(cnfClause);
			return cnf;
		}
		if (!Connective.AND.equals(connective)) {
			return null;
		}
		CNF cnf = new CNF();
		for (Expression e : expressions) {
			if ((e instanceof MultaryConnectiveExpression)) {
				MultaryConnectiveExpression clause = (MultaryConnectiveExpression) e;
				int[] cnfClause = new int[clause.expressions.size()];
				for (int i = 0; i < clause.expressions.size(); i++) {
					Expression it = clause.expressions.get(i);
					if (it instanceof Atom) {
						int variable = cnf.shallowComputeIfAbsent(it);
						cnfClause[i] = variable;
					} else if (it instanceof NegatedExpression) {
						int variable = cnf.shallowComputeIfAbsent(((NegatedExpression) it).getAtom());
						cnfClause[i] = -variable;
					} else {
						return null;
					}
				}
				cnf.add(cnfClause);
			} else if (e instanceof Atom) {
				cnf.add(cnf.shallowComputeIfAbsent(e));
			} else if (e instanceof NegatedExpression) {
				cnf.add(-cnf.shallowComputeIfAbsent(((NegatedExpression) e).getAtom()));
			} else {
				return null;
			}
		}
		return cnf;
	}

	@Override
	public Expression standardize(Map<Long, Long> map, IntIdGenerator generator) {
		return new MultaryConnectiveExpression(
			connective,
			expressions.stream().map(t -> t.standardize(map, generator)).collect(Collectors.toList())
		);
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

	@Override
	public boolean equals(Object o) {
		if (this == o) return true;
		if (o == null || getClass() != o.getClass()) return false;

		MultaryConnectiveExpression that = (MultaryConnectiveExpression) o;

		if (connective != that.connective) return false;
		return expressions.equals(that.expressions);
	}

	@Override
	public int hashCode() {
		int result = connective.hashCode();
		result = 31 * result + expressions.hashCode();
		return result;
	}
}
