package it.unibz.stud_inf.ils.white.prisma.ast;

import com.google.common.collect.Sets;
import it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm;
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
import static it.unibz.stud_inf.ils.white.prisma.ast.ConnectiveExpression.Connective.AND;
import static it.unibz.stud_inf.ils.white.prisma.ast.ConnectiveExpression.Connective.ITE;
import static it.unibz.stud_inf.ils.white.prisma.ast.ConnectiveExpression.Connective.NOT;
import static it.unibz.stud_inf.ils.white.prisma.ast.ConnectiveExpression.Connective.OR;
import static java.util.Collections.emptySet;
import static java.util.stream.Collectors.joining;
import static java.util.stream.Collectors.toList;

public class ConnectiveExpression extends Expression {
	public Connective getConnective() {
		return connective;
	}

	private final Connective connective;
	private final List<Expression> expressions;

	public ConnectiveExpression(Connective connective, List<Expression> expressions) {
		if (expressions.stream().anyMatch(Objects::isNull)) {
			throw new NullPointerException();
		}
		this.expressions = expressions;
		this.connective = connective;
	}

	public ConnectiveExpression(Connective connective, Expression... expressions) {
		int enforcedArity = connective.getEnforcedArity();
		if (enforcedArity != 0 && enforcedArity != expressions.length) {
			throw new IllegalArgumentException("Refusing multary connective");
		}
		this.connective = connective;
		this.expressions = Arrays.asList(expressions);
		if (stream().anyMatch(Objects::isNull)) {
			throw new NullPointerException();
		}
	}

	public ConnectiveExpression(Expression left, Connective connective, Expression right) {
		this(connective, left, right);
	}

	public ConnectiveExpression compress() {
		if (expressions.stream().allMatch(e -> {
			return (e instanceof ConnectiveExpression) && ((ConnectiveExpression) e).connective.equals(connective);
		})) {
			return new ConnectiveExpression(
				connective,
				stream().flatMap(e -> ((ConnectiveExpression) e).expressions.stream()).collect(toList())
			);
		}
		return this;
	}

	private void assertSimple() {
		int enforcedArity = connective.getEnforcedArity();
		if (enforcedArity != 2 && enforcedArity != 0) {
			throw new IllegalStateException("Connective is not simple.");
		}
		if (expressions.size() != 2) {
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

	public ConnectiveExpression swap(Expression... expressions) {
		return swap(Arrays.asList(expressions));
	}

	public ConnectiveExpression swap(List<Expression> expressions) {
		return new ConnectiveExpression(connective, expressions);
	}

	public boolean isClause() {
		return is(OR) && stream().allMatch(Expression::isLiteral);
	}

	public boolean is(Connective connective) {
		return connective.equals(this.connective);
	}

	@Override
	public String toString() {
		int enforcedArity = connective.getEnforcedArity();

		if (enforcedArity == 0) {
			return stream()
				.map(Object::toString)
				.collect(joining(" " + connective + " ", "(", ")"));
		}

		if (is(ITE)) {
			return "(" + expressions.get(0) + " ? " + expressions.get(1) + " : " + expressions.get(2) + ")";
		}

		if (is(NOT)) {
			return "~" + expressions.get(0);
		}

		if (enforcedArity == 2) {
			return "(" + expressions.get(0) + " " + connective + " " + expressions.get(1) + ")";
		}

		throw new RuntimeException("How did I get here?");
	}

	@Override
	public Expression pushQuantifiersDown() {
		return new ConnectiveExpression(
			connective,
			stream()
				.map(Expression::pushQuantifiersDown)
				.collect(toList())
		).compress();
	}

	@Override
	public Expression normalize() {
		int enforcedArity = connective.getEnforcedArity();
		if (enforcedArity != 0 && enforcedArity != expressions.size()) {
			throw new UnsupportedOperationException();
		}

		if (is(NOT)) {
			final var subExpression = expressions.get(0);
			if (subExpression instanceof Atom) {
				return not(subExpression.normalize());
			}
			if ((subExpression instanceof ConnectiveExpression)) {
				ConnectiveExpression subMultary = (ConnectiveExpression) subExpression;
				if (subMultary.is(NOT)) {
					return subMultary.expressions.get(0).normalize();
				}
			}
			return subExpression.normalize().deMorgan();
		}

		// From here on we assume enforcedArity == expressions.size()

		if (is(ITE)) {
			final var condition = expressions.get(0);
			final var truthy = expressions.get(1);
			final var falsy = expressions.get(2);
			return and(
				or(not(condition).normalize(), truthy.normalize()),
				or(condition.normalize(), falsy.normalize())
			);
		}

		final var left = getLeft();
		final var right = getRight();

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
		Stream<Expression> groundExpressions = stream()
			.map(e -> e.ground(substitution));

		if (is(AND) || is(OR)) {
			groundExpressions = groundExpressions.filter(e -> {
				return !(e.equals(getIdentity()));
			});
		}

		return swap(groundExpressions.collect(toList())).compress();
	}

	public Expression getIdentity() {
		if (!is(AND) && !is(OR)) {
			throw new UnsupportedOperationException("Identity is only defined for AND and OR.");
		}
		return is(AND) ? TRUE : FALSE;
	}

	@Override
	public Integer tseitin(ConjunctiveNormalForm cnf) {
		if (is(NOT)) {
			final var subExpression = expressions.get(0);

			if (!(subExpression instanceof Atom)) {
				throw new IllegalStateException("Formula must be in negation normal form.");
			}

			return -cnf.computeIfAbsent(subExpression);
		}

		if (!is(OR) && !is(AND)) {
			throw new UnsupportedOperationException("Tseitin translation is only defined for AND and OR.");
		}

		List<Integer> variables = stream().map(cnf::computeIfAbsent).collect(toList());

		Integer self = cnf.put(this);

		int factor = is(AND) ? -1 : 1;

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
		if (is(NOT)) {
			return expressions.get(0);
		}

		return new ConnectiveExpression(
			is(AND) ? OR : AND,
			stream()
				.map(Expression::deMorgan)
				.collect(toList())
		);
	}

	public ConjunctiveNormalForm tseitinFast() {
		// If this is a disjunction, continue under
		// the assumption that this is a clause.
		if (is(OR)) {
			final var cnf = new ConjunctiveNormalForm();
			int[] cnfClause = new int[expressions.size()];
			for (int i = 0; i < expressions.size(); i++) {
				final var it = expressions.get(i);

				if (!it.isLiteral()) {
					return null;
				}
				if (it instanceof Atom) {
					int variable = cnf.shallowComputeIfAbsent(it);
					cnfClause[i] = variable;
				} else {
					int variable = cnf.shallowComputeIfAbsent(((ConnectiveExpression) it).expressions.get(0));
					cnfClause[i] = -variable;
				}
			}
			cnf.add(cnfClause);
			return cnf;
		}

		if (!is(AND)) {
			return null;
		}

		// Continue under the assumption that this is a conjunction of clauses.
		ConjunctiveNormalForm cnf = new ConjunctiveNormalForm();
		for (Expression e : expressions) {
			if (e.isLiteral()) {
				if (e instanceof Atom) {
					cnf.add(cnf.shallowComputeIfAbsent(e));
				} else {
					cnf.add(-cnf.shallowComputeIfAbsent(((ConnectiveExpression) e).expressions.get(0)));
				}
				continue;
			}

			if ((e instanceof ConnectiveExpression)) {
				ConnectiveExpression clause = (ConnectiveExpression) e;
				int[] cnfClause = new int[clause.expressions.size()];
				for (int i = 0; i < clause.expressions.size(); i++) {
					Expression it = clause.expressions.get(i);

					if (!it.isLiteral()) {
						return null;
					}

					if (it instanceof Atom) {
						int variable = cnf.shallowComputeIfAbsent(it);
						cnfClause[i] = variable;
					} else {
						int variable = cnf.shallowComputeIfAbsent(((ConnectiveExpression) it).expressions.get(0));
						cnfClause[i] = -variable;
					}
				}
				cnf.add(cnfClause);
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
		THEN("->", 2),
		IFF("<->", 2),
		IF("<-", 2),
		AND("&", 0),
		OR("|", 0),
		XOR("^", 2),
		ITE("?:", 3),
		NOT("~", 1);

		private final String asString;
		private final int enforcedArity;

		Connective(String asString, int enforcedArity) {
			this.asString = asString;
			this.enforcedArity = enforcedArity;
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

		public int getEnforcedArity() {
			return enforcedArity;
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

		ConnectiveExpression that = (ConnectiveExpression) o;

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

	@Override
	public Set<Set<Variable>> getRelatedVariables() {
		return expressions
			.stream()
			.map(Expression::getRelatedVariables)
			.reduce(emptySet(), Sets::union);
	}

	private Stream<Expression> stream() {
		return expressions.stream();
	}

	private ConnectiveExpression map(Function<? super Expression, ? extends Expression> f) {
		return swap(stream().map(f).collect(toList()));
	}

	@Override
	public boolean isLiteral() {
		return is(NOT) && (expressions.get(0) instanceof Atom);
	}
}
