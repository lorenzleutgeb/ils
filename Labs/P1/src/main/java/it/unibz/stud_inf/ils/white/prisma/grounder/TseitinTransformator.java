package it.unibz.stud_inf.ils.white.prisma.grounder;

import java.util.*;

public class TseitinTransformator {
	private Integer counter = 1;

	public Map<Expression, Integer> fmVars;
	public Set<Set<Integer>> clauses;

	public TseitinTransformator() {
		fmVars = new HashMap<Expression, Integer>();
		clauses = new HashSet<Set<Integer>>();
	}

	Set<Set<Integer>> getClauses() {
		return clauses;
	}

	/*
	Expression getResultExpression(Integer x) {
		List<Expression> clfms = new LinkedList<Expression>();
		clfms.add(var (new Var(x)));
		for (Set<Integer> c : clauses) {
			List<Expression> lits = new LinkedList<Expression>();
			for (Integer y : c) {
				if (y > 0) {
					lits.add(var(new Var(y)));
				} else {
					lits.add(neg(var(new Var(-y))));
				}
			}
			clfms.add(or(lits));
		}
		return and(clfms);
	}

	String getResultDIMACS(Integer x) {
		StringBuffer s = new StringBuffer();
		s.append("fm " + (clauses.size() + 1) + " " + nextName + "\n");
		s.append(x + " 0\n");
		for (Set<Integer> c : clauses) {
			for (Integer y : c) {
				s.append(y);
				s.append(" ");
			}
			s.append("0\n");
		}
		return s.toString();
	}
*/
	public Integer visit(Expression expr) {
		if (expr instanceof BinaryConnectiveExpression) {
			switch (((BinaryConnectiveExpression)expr).getConnective()) {
				case AND:
					return visitAnd((BinaryConnectiveExpression) expr);
				case OR:
					return visitOr((BinaryConnectiveExpression) expr);
			}
			throw new UnsupportedOperationException();
		} else if (expr instanceof NegatedExpression) {
			return visitNeg((NegatedExpression) expr);
		} else if (expr instanceof Atom) {
			return fmVars.computeIfAbsent(expr, expression -> freshName());
		} else {
			throw new UnsupportedOperationException();
		}
	}

	/*
	public Integer visitVar(ExpressionVar fm) {
		fmVars.put(fm, fm.name.number);
		return fm.name.number;
	}*/

	public Integer visitNeg(NegatedExpression fm) {
		Integer xbody = fmVars.get(fm.getSubExpression());
		if (xbody == null) {
			xbody = visit(fm.getSubExpression());
		}
		Integer x = freshName();
		fmVars.put(fm, x);
		Set<Integer> clause = new TreeSet<Integer>();
		clause.add(x);
		clause.add(xbody);
		clauses.add(clause);
		clause = new TreeSet<Integer>();
		clause.add(-x);
		clause.add(-xbody);
		clauses.add(clause);
		return x;
	}

	public Integer visitOr(BinaryConnectiveExpression expr) {
		Integer left = fmVars.get(expr.getLeft());
		if (left == null) {
			left = visit(expr.getLeft());
			fmVars.put(expr.getLeft(), left);
		}
		Integer right = fmVars.get(expr.getRight());
		if (right == null) {
			right = visit(expr.getRight());
			fmVars.put(expr.getRight(), right);
		}

		Integer x = freshName();
		fmVars.put(expr, x);

		Set<Integer> clause = new TreeSet<Integer>();
		clause.add(-x);
		clause.add(left);
		clause.add(right);
		clauses.add(clause);


		clause = new TreeSet<Integer>();
		clause.add(x);
		clause.add(-left);
		clauses.add(clause);

		clause = new TreeSet<Integer>();
		clause.add(x);
		clause.add(-right);
		clauses.add(clause);

		return x;
	}

	public Integer visitAnd(BinaryConnectiveExpression expr) {
		Integer left = fmVars.get(expr.getLeft());
		if (left == null) {
			left = visit(expr.getLeft());
			fmVars.put(expr.getLeft(), left);
		}
		Integer right = fmVars.get(expr.getRight());
		if (right == null) {
			right = visit(expr.getRight());
			fmVars.put(expr.getRight(), right);
		}

		Integer x = freshName();
		fmVars.put(expr, x);

		Set<Integer> clause = new TreeSet<Integer>();
		clause.add(x);
		clause.add(-left);
		clause.add(-right);
		clauses.add(clause);

		clause = new TreeSet<Integer>();
		clause.add(-x);
		clause.add(left);
		clauses.add(clause);

		clause = new TreeSet<Integer>();
		clause.add(-x);
		clause.add(right);
		clauses.add(clause);

		return x;
	}

	private Integer freshName() {
		return counter++;
	}
}

