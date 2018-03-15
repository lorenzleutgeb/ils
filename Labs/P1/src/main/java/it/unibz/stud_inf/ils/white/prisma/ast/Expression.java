package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.CNF;
import it.unibz.stud_inf.ils.white.prisma.Groundable;

public abstract class Expression implements Groundable<Expression> {
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

	public CNF initialize() {
		CNF cnf = new CNF();

		// Assumption: Expression is ground!
		Integer root = normalize(cnf);
		cnf.put(this, root);

		// Ensure that the formula itself is true in every model.
		cnf.add(root);

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
}
