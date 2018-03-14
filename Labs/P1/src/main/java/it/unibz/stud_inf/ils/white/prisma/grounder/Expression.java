package it.unibz.stud_inf.ils.white.prisma.grounder;

public abstract class Expression implements Groundable<Expression> {
	public Expression compress(Expression left, BinaryConnectiveExpression.Connective connective, Expression right) {
		// This should implement some basic compression of the AST. For example,
		// a | ~a  ->  true
		// a & ~a  ->  false
		// a | true  ->  true
		// a | false  ->  a
		// ...
		throw new UnsupportedOperationException("Not implemented.");
	}
}
