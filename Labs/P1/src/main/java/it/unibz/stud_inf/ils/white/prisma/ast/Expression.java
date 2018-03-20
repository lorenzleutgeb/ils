package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm;
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

	public abstract Integer tseitin(ConjunctiveNormalForm cnf);

	public ConjunctiveNormalForm tseitin() {
		// Are we already in CNF by chance?
		ConjunctiveNormalForm cnf = tseitinFast(this);

		// Fast path did not yield a result, use Tseitin.
		if (cnf != null) {
			return cnf;
		}

		cnf = new ConjunctiveNormalForm();

		// Assumption: Expression is ground!
		Integer root = tseitin(cnf);
		cnf.put(this, root);

		// Ensure that the formula itself is true in every model.
		cnf.add(root);

		return cnf;
	}

	public static ConjunctiveNormalForm tseitinFast(Expression expression) {
		// Assumption: Formula is ground and in NNF.
		if (expression instanceof Atom) {
			ConjunctiveNormalForm cnf = new ConjunctiveNormalForm();
			Integer atom = cnf.put(expression);
			cnf.add(atom);
			return cnf;
		}
		if (expression instanceof NegatedExpression) {
			ConjunctiveNormalForm cnf = new ConjunctiveNormalForm();
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

	public Set<Set<Variable>> getRelatedVariables()  {
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
