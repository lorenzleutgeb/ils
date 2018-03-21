package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.ConjunctiveNormalForm;
import it.unibz.stud_inf.ils.white.prisma.Groundable;

import java.util.Set;

import static it.unibz.stud_inf.ils.white.prisma.ast.ConnectiveExpression.Connective.AND;
import static it.unibz.stud_inf.ils.white.prisma.ast.ConnectiveExpression.Connective.NOT;
import static it.unibz.stud_inf.ils.white.prisma.ast.ConnectiveExpression.Connective.OR;

public abstract class Expression implements Groundable<Expression, Expression> {
	public Expression compress(Expression left, ConnectiveExpression.Connective connective, Expression right) {
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

	public static ConjunctiveNormalForm tseitinFast(Expression expression) {
		// Assumption: Formula is ground and in NNF.
		if (expression instanceof ConnectiveExpression) {
			if (expression.isLiteral()) {
				ConjunctiveNormalForm cnf = new ConjunctiveNormalForm();
				Integer atom = cnf.put(((ConnectiveExpression)expression).getExpressions().get(0));
				cnf.add(-atom);
				return cnf;
			} else {
				return ((ConnectiveExpression)expression).tseitinFast();
			}
		}

		if (!(expression instanceof Atom)) {
			return null;
		}

		ConjunctiveNormalForm cnf = new ConjunctiveNormalForm();
		Integer atom = cnf.put(expression);
		cnf.add(atom);
		return cnf;
	}

	@Override
	public Set<Variable> getOccurringVariables() {
		throw new UnsupportedOperationException();
	}

	public Set<Set<Variable>> getRelatedVariables()  {
		throw new UnsupportedOperationException();
	}

	public static ConnectiveExpression and(Expression left, Expression right) {
		return new ConnectiveExpression(
			left,
			AND,
			right
		);
	}

	public static ConnectiveExpression or(Expression left, Expression right) {
		return new ConnectiveExpression(
			left,
			OR,
			right
		);
	}

	public static ConnectiveExpression not(Expression expression) {
		return new ConnectiveExpression(
			NOT,
			expression
		);
	}

	public boolean isLiteral() {
		return false;
	}
}
