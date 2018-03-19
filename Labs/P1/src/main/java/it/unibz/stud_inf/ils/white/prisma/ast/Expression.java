package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.Groundable;

import java.util.Set;

public abstract class Expression implements Groundable<Expression, Expression> {
	public Expression compress(Expression left, MultaryConnectiveExpression.Connective connective, Expression right) {
		// This should implement some basic compression of the AST. For example,
		// a | ~a  ->  true
		// a & ~a  ->  false
		// a | true  ->  true
		// a | false  ->  a
		// ...
		throw new UnsupportedOperationException("Not implemented.");
	}

	public Expression normalize() {
		return this;
	}

	public Expression deMorgan() {
		return this;
	}

	public Expression pushQuantifiersDown() {
		return this;
	}

	public abstract Integer tseitin(it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm cnf);

	public it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm tseitin() {
		// Are we already in CNF by chance?
		it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm cnf = tseitinFast(this);

		// Fast path did not yield a result, use Tseitin.
		if (cnf != null) {
			return cnf;
		}

		cnf = new it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm();

		// Assumption: Expression is ground!
		Integer root = tseitin(cnf);
		cnf.put(this, root);

		// Ensure that the formula itself is true in every model.
		cnf.add(root);

		return cnf;
	}

	public static it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm tseitinFast(Expression expression) {
		// Assumption: Formula is ground and in NNF.
		if (expression instanceof Atom) {
			it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm cnf = new it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm();
			Integer atom = cnf.put(expression);
			cnf.add(atom);
			return cnf;
		}
		if (expression instanceof NegatedExpression) {
			it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm cnf = new it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm();
			Integer atom = cnf.put(((NegatedExpression)expression).getAtom());
			cnf.add(-atom);
			return cnf;
		}
		if (!(expression instanceof MultaryConnectiveExpression)) {
			return null;
		}
		return ((MultaryConnectiveExpression)expression).tseitinFast();
	}

	@Override
	public Set<Variable> getOccurringVariables() {
		throw new UnsupportedOperationException();
	}

	public static MultaryConnectiveExpression and(Expression left, Expression right) {
		return new MultaryConnectiveExpression(
			left,
			MultaryConnectiveExpression.Connective.AND,
			right
		);
	}

	public static MultaryConnectiveExpression or(Expression left, Expression right) {
		return new MultaryConnectiveExpression(
			left,
			MultaryConnectiveExpression.Connective.OR,
			right
		);
	}

	public static NegatedExpression not(Expression expression) {
		return new NegatedExpression(expression);
	}
}
