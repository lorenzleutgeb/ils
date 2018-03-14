package it.unibz.stud_inf.ils.white.prisma.solver;

import it.unibz.stud_inf.ils.white.prisma.grounder.Expression;
import it.unibz.stud_inf.ils.white.prisma.grounder.Formula;
import it.unibz.stud_inf.ils.white.prisma.grounder.TseitinTransformator;
import org.sat4j.core.ASolverFactory;
import org.sat4j.core.VecInt;
import org.sat4j.minisat.SolverFactory;
import org.sat4j.specs.ContradictionException;
import org.sat4j.specs.ISolver;
import org.sat4j.specs.TimeoutException;

import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

public class Solver {
	public static void solve(Formula f) {
		solve(f.ground());
	}

	public static void solve(Expression expr) {
		ISolver solver = SolverFactory.newDefault();

		TseitinTransformator transformator = new TseitinTransformator();
		Integer root = transformator.visit(expr);

		try {
			solver.addClause(new VecInt(new int[]{root}));
		} catch (ContradictionException e) {
			e.printStackTrace();
		}

		for (Map.Entry<Expression, Integer> entry : transformator.fmVars.entrySet()) {
			//System.out.println(entry.getValue() + "\t-> " + entry.getKey());
		}

		for (Set<Integer> clause : transformator.clauses) {
			try {
				solver.addClause(new VecInt(clauseToArray(clause)));
			} catch (ContradictionException e) {
				System.out.println("UNSAT!");
				return;
			}
			//System.out.println(clause.stream().map(String::valueOf).collect(Collectors.joining(" ")));
		}

		try {
			if (solver.isSatisfiable()) {
				for (Integer literal : solver.model()) {
					for (Map.Entry<Expression, Integer> entry : transformator.fmVars.entrySet()) {
						if (Math.abs(literal) == entry.getValue()) {
							System.out.println((literal > 0 ? "TRUE" : "FALSE") + " -> " + entry.getKey());
						}
					}
				}
			} else {
				System.out.println("UNSAT!");
			}
		} catch (TimeoutException e) {
			e.printStackTrace();
		}
	}

	private static int[] clauseToArray(Set<Integer> clause) {
		int[] arr = new int[clause.size()];

		int index = 0;
		for(Integer i : clause) {
			arr[index++] = i; //note the autounboxing here
		}

		return arr;
	}
}
