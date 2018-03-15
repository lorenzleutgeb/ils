package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.CNF;
import it.unibz.stud_inf.ils.white.prisma.Groundable;
import it.unibz.stud_inf.ils.white.prisma.IntIdGenerator;

import java.util.Map;

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

	public abstract Integer normalize(CNF cnf);

	public CNF normalize() {
		// Are we already in CNF by chance?
		CNF cnf = normalizeFast(this);

		// Fast path did not yield a result, use Tseitin.
		if (cnf == null) {
			cnf = new CNF();

			// Assumption: Expression is ground!
			Integer root = normalize(cnf);
			cnf.put(this, root);

			// Ensure that the formula itself is true in every model.
			cnf.add(root);
		}

		// Ensure that "true" is true in every model.
		Integer t = cnf.get(Atom.TRUE);
		if (t != null) {
			cnf.add(t);
		}

		// Ensure that "false" is false in every model.
		Integer f = cnf.get(Atom.FALSE);
		if (f != null) {
			cnf.add(-f);
		}

		return cnf;
	}

	private static CNF normalizeFast(Expression expression) {
		// Assumption: Formula is ground and in NNF.
		if (expression instanceof Atom) {
			CNF cnf = new CNF();
			Integer atom = cnf.put(expression);
			cnf.add(atom);
			return cnf;
		}
		if (expression instanceof NegatedExpression) {
			CNF cnf = new CNF();
			Integer atom = cnf.put(((NegatedExpression)expression).getAtom());
			cnf.add(-atom);
			return cnf;
		}
		if (!(expression instanceof MultaryConnectiveExpression)) {
			return null;
		}
		return ((MultaryConnectiveExpression)expression).normalizeFast();
	}

	public abstract Expression deMorgan();
}
