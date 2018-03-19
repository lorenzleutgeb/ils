package it.unibz.stud_inf.ils.white.prisma.ast;

import com.google.common.collect.Sets;
import it.unibz.stud_inf.ils.white.prisma.Groundable;
import it.unibz.stud_inf.ils.white.prisma.IntIdGenerator;
import it.unibz.stud_inf.ils.white.prisma.Substitution;

import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Stream;

import static it.unibz.stud_inf.ils.white.prisma.ast.Atom.FALSE;
import static it.unibz.stud_inf.ils.white.prisma.ast.Atom.TRUE;
import static java.util.Collections.emptySet;
import static java.util.stream.Collectors.joining;
import static java.util.stream.Collectors.toList;

public class MultaryConnectiveExpression extends Expression {
	public Connective getConnective() {
		return connective;
	}

	private final Connective connective;
	private final List<Expression> expressions;

	public MultaryConnectiveExpression(Connective connective, List<Expression> expressions) {
		if (expressions.stream().anyMatch(Objects::isNull)) {
			throw new NullPointerException();
		}
		this.expressions = expressions;
		this.connective = connective;
	}

	public MultaryConnectiveExpression(Connective connective, Expression... expressions) {
		if (expressions.length != 2 && !(Connective.AND.equals(connective) || Connective.OR.equals(connective))) {
			throw new IllegalArgumentException("Refusing multary connective");
		}
		this.connective = connective;
		this.expressions = Arrays.asList(expressions);
		if (stream().anyMatch(Objects::isNull)) {
			throw new NullPointerException();
		}
	}

	public MultaryConnectiveExpression(Expression left, Connective connective, Expression right) {
		this(connective, left, right);
	}

	public MultaryConnectiveExpression compress() {
		if (expressions.stream().allMatch(e -> {
			return (e instanceof MultaryConnectiveExpression) && ((MultaryConnectiveExpression) e).connective.equals(connective);
		})) {
			return new MultaryConnectiveExpression(
				connective,
				stream().flatMap(e -> ((MultaryConnectiveExpression) e).expressions.stream()).collect(toList())
			);
		}
		return this;
	}

	private void assertSimple() {
		if (expressions.size() != 2 && !(Connective.AND.equals(connective) || Connective.OR.equals(connective))) {
			throw new IllegalArgumentException("Refusing multary connective");
		}
	}

	public Expression getLeft() {
		assertSimple();
		return expressions.get(0);
	}

	public Expression getRight() {
		assertSimple();
		return expressions.get(1);
	}

	public MultaryConnectiveExpression swap(Expression... expressions) {
		return swap(Arrays.asList(expressions));
	}

	public MultaryConnectiveExpression swap(List<Expression> expressions) {
		return new MultaryConnectiveExpression(connective, expressions);
	}

	public boolean isClause() {
		if (!Connective.OR.equals(connective)) {
			return false;
		}
		return stream()
			.allMatch(e -> ((e instanceof Atom) || (e instanceof NegatedExpression)));
	}

	@Override
	public String toString() {
		return stream()
			.map(Object::toString)
			.collect(joining(" " + connective + " ", "(", ")"));
	}

	@Override
	public Expression pushQuantifiersDown() {
		return new MultaryConnectiveExpression(
			connective,
			stream()
				.map(Expression::pushQuantifiersDown)
				.collect(toList())
		).compress();
		/*
		if (expressions.size() != 2 && (Connective.AND.equals(connective) || Connective.OR.equals(connective))) {
			throw new UnsupportedOperationException();
		}

		Expression l = expressions.get(0).pushQuantifiersDown();
		Expression r = expressions.get(1).pushQuantifiersDown();

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
					).pushQuantifiersDown()
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
			).pushQuantifiersDown()
		);*/
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
				return or(not(left).normalize(), right.normalize());
			case IFF:
				return and(
					or(not(left).normalize(), right.normalize()),
					or(not(right).normalize(), left.normalize())
				);
			case IF:
				return or(left.normalize(), not(right).normalize());
			case XOR:
				return and(
					or(left, right).normalize(),
					or(not(left), not(right)).normalize()
				);
			default:
				return swap(left.normalize(), right.normalize());
		}
	}

	@Override
	public Expression ground(Substitution substitution) {
		return new MultaryConnectiveExpression(
			connective,
			stream()
				.map(e -> e.ground(substitution))
				.filter(e -> {
					return !(e.equals(getIdentity()));
				})
				.collect(toList())
		).compress();
	}

	public Expression getIdentity() {
		if (!Connective.AND.equals(connective) && !Connective.OR.equals(connective)) {
			throw new UnsupportedOperationException();
		}
		return Connective.AND.equals(connective) ? TRUE : FALSE;
	}

	@Override
	public Integer tseitin(it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm cnf) {
		if (!connective.equals(Connective.OR) && !connective.equals(Connective.AND)) {
			throw new IllegalStateException();
		}

		List<Integer> variables = stream().map(cnf::computeIfAbsent).collect(toList());

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
			stream()
				.map(Expression::deMorgan)
				.collect(toList())
		);
	}

	public it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm tseitinFast() {
		if (Connective.OR.equals(connective)) {
			it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm cnf = new it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm();
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
		it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm cnf = new it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm();
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
		return map(t -> t.standardize(map, generator));
	}

	public List<Expression> getExpressions() {
		return expressions;
	}

	public enum Connective {
		THEN("->"),
		IFF("<->"),
		IF("<-"),
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
		if (this == o) {
			return true;
		}
		if (o == null || getClass() != o.getClass()) {
			return false;
		}

		MultaryConnectiveExpression that = (MultaryConnectiveExpression) o;

		if (connective != that.connective) {
			return false;
		}
		return expressions.equals(that.expressions);
	}

	@Override
	public int hashCode() {
		int result = connective.hashCode();
		result = 31 * result + expressions.hashCode();
		return result;
	}

	@Override
	public Set<Variable> getOccurringVariables() {
		return expressions
			.stream()
			.map(Groundable::getOccurringVariables)
			.reduce(emptySet(), Sets::union);
	}

	private Stream<Expression> stream() {
		return expressions.stream();
	}

	private MultaryConnectiveExpression map(Function<? super Expression, ? extends Expression> f) {
		return swap(stream().map(f).collect(toList()));
	}
}
