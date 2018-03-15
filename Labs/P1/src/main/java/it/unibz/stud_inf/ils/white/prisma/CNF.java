package it.unibz.stud_inf.ils.white.prisma;

import com.google.common.collect.BiMap;
import com.google.common.collect.HashBiMap;
import it.unibz.stud_inf.ils.white.prisma.ast.Atom;
import it.unibz.stud_inf.ils.white.prisma.ast.Expression;
import org.sat4j.core.Vec;
import org.sat4j.core.VecInt;
import org.sat4j.minisat.SolverFactory;
import org.sat4j.specs.*;
import org.sat4j.tools.ModelIterator;

import java.io.PrintStream;
import java.util.*;
import java.util.stream.Collectors;

public class CNF {
	private final BiMap<Expression, Integer> map;
	private final IVec<IVecInt> clauses;
	private int maxVariable = 1;

	public CNF() {
		this.map = HashBiMap.create();
		this.clauses = new Vec<>();
	}

	public Expression get(Integer variable) {
		return map.inverse().get(variable);
	}

	public Integer get(Expression expression) {
		return map.get(expression);
	}

	public Integer put(Expression expression, Integer variable) {
		if (variable <= 0) {
			throw new IllegalArgumentException("variable must be positive non-zero integer");
		}
		return map.put(expression, variable);
	}

	public Integer computeIfAbsent(Expression expression) {
		Integer variable = get(expression);
		if (variable == null) {
			variable = expression.normalize(this);
			put(expression, variable);
			return variable;
		}
		return variable;
	}

	public IVec<IVecInt> getClauses() {
		return clauses;
	}

	public IVec<IVecInt> add(int... literals) {
		return clauses.push(new VecInt(literals));
	}

	public Integer put(Expression expression) {
		int variable = maxVariable++;
		map.put(expression, variable);
		return variable;
	}

	public Set<Atom> translate(int[] model) {
		Set<Atom> set = new HashSet<>();
		for (Integer literal : model) {
			if (literal < 0) {
				continue;
			}

			Expression e = get(literal);

			if (e instanceof Atom && !Atom.TRUE.equals(e)) {
				set.add((Atom) e);
			}
		}
		return set;
	}

	public void printDimacsTo(PrintStream out) {
		for (Map.Entry<Integer, Expression> entry : map.inverse().entrySet()) {
			if (filter(entry.getValue())) {
				out.println("c " + entry.getKey() + " " + entry.getValue());
			}
		}
		out.println("p cnf " + maxVariable + " " + clauses.size());
		for (int i = 0; i < clauses.size(); i++) {
			IVecInt clause = clauses.get(i);
			for (int j = 0; j < clause.size(); j++) {
				out.print(clause.get(j));

				if (j != clause.size() - 1) {
					out.print(" ");
				}
			}
			out.println(" 0");
		}
	}

	public void printTo(PrintStream out) {
		for (int i = 0; i < clauses.size(); i++) {
			IVecInt clause = clauses.get(i);
			out.print("( ");
			for (int j = 0; j < clause.size(); j++) {
				Integer literal = clause.get(j);

				if (literal < 0) {
					out.print("~");
				}

				Integer variable = Math.abs(literal);
				Expression expression = get(variable);

				if (filter(expression)) {
					out.print(expression);
				} else {
					out.print("subformula" + variable);
				}

				if (j != clause.size() - 1) {
					out.print(" | ");
				}
			}
			if (i != clauses.size() - 1) {
				out.println(" ) &");
			} else {
				out.println(" )");
			}
		}
	}

	public void printModelsTo(PrintStream out, long n) {
		List<Set<Atom>> models = solve(n);

		if (models.isEmpty()) {
			out.println("UNSAT");
		}

		for (Set<Atom> model : models) {
			out.println(model.stream().map(Object::toString).collect(Collectors.joining(", ", "{", "}")));
		}
	}

	public Set<Atom> model() {
		List<Set<Atom>> models = models(1);
		if (models.isEmpty()) {
			return null;
		}
		return models.get(0);
	}

	public List<Set<Atom>> models(long n) {
		return solve(n);
	}

	public List<Set<Atom>> models() {
		return solve(Long.MAX_VALUE);
	}

	private List<Set<Atom>> solve(long n) {
		ISolver solver = SolverFactory.newDefault();

		try {
			solver.addAllClauses(getClauses());
		} catch (ContradictionException e) {
			return Collections.emptyList();
		}

		ISolver iterator = new ModelIterator(solver, n);

		try {
			List<Set<Atom>> models = new ArrayList<>();
			while (iterator.isSatisfiable()) {
				models.add(translate(iterator.model()));
			}
			return models;
		} catch (TimeoutException e) {
			e.printStackTrace();
		}

		throw new RuntimeException("How did I get here?");
	}

	public String getStats() {
		return maxVariable + " " + clauses.size();
	}

	private static boolean filter(Expression e) {
		return e instanceof Atom && !Atom.TRUE.equals(e) && !Atom.FALSE.equals(e);
	}
}
