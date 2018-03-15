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

import static it.unibz.stud_inf.ils.white.prisma.Util.SET_COLLECTOR;

public class CNF {
	private final BiMap<String, Integer> map;
	private final IVec<IVecInt> clauses;
	private final IntIdGenerator generator = new IntIdGenerator(1);

	public CNF() {
		this.map = HashBiMap.create();
		this.clauses = new Vec<>();
	}

	private String get(Integer variable) {
		return map.inverse().get(variable);
	}

	public Integer get(Expression expression) {
		return map.get(key(expression));
	}

	public Integer put(Expression expression, Integer variable) {
		//if (variable <= 0) {
		//	throw new IllegalArgumentException("variable must be positive non-zero integer");
		//}
		return map.put(key(expression), variable);
	}

	public Integer computeIfAbsent(Expression expression) {
		Integer variable = get(expression);
		if (variable == null) {
			variable = expression.tseitin(this);
			put(expression, variable);
			return variable;
		}
		return variable;
	}

	public Integer shallowComputeIfAbsent(Expression expression) {
		Integer variable = get(expression);
		if (variable == null) {
			variable = generator.getNextId();
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
		int variable = generator.getNextId();
		map.put(key(expression), variable);
		return variable;
	}

	private static String key(Expression e) {
		String key = e.toString();
		if (e instanceof Atom) {
			key = ":" + key;
		}
		return key;
	}

	public Set<String> translate(int[] model) {
		Set<String> set = new HashSet<>();
		for (Integer literal : model) {
			if (literal < 0) {
				continue;
			}

			String e = get(literal);

			if (filter(e)) {
				set.add(e.substring(1));
			}
		}
		return set;
	}

	public void printDimacsTo(PrintStream out) {
		for (Map.Entry<Integer, String> entry : map.inverse().entrySet()) {
			if (filter(entry.getValue())) {
				out.println("c " + entry.getKey() + " " + entry.getValue());
			}
		}
		out.println("p cnf " + getStats());
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
			out.print("(");
			for (int j = 0; j < clause.size(); j++) {
				Integer literal = clause.get(j);

				if (literal < 0) {
					out.print("~");
				}

				Integer variable = Math.abs(literal);
				String expression = get(variable);

				if (expression.startsWith(":")) {
					out.print(expression.substring(1));
				} else {
					out.print("subformula" + variable);
				}

				if (j != clause.size() - 1) {
					out.print(" | ");
				}
			}
			if (i != clauses.size() - 1) {
				out.println(") &");
			} else {
				out.println(")");
			}
		}
	}

	public void printModelsTo(PrintStream out, long n) {
		List<Set<String>> models = solve(n);

		if (models.isEmpty()) {
			out.println("UNSAT");
		}

		for (Set<String> model : models) {
			out.println(model.stream().collect(SET_COLLECTOR));
		}
	}

	public void printModelsTo(PrintStream out) {
		printModelsTo(out, Long.MAX_VALUE);
	}

	public Set<String> model() {
		List<Set<String>> models = models(1);
		if (models.isEmpty()) {
			return null;
		}
		return models.get(0);
	}

	public List<Set<String>> models(long n) {
		return solve(n);
	}

	public List<Set<String>> models() {
		return solve(Long.MAX_VALUE);
	}

	private List<Set<String>> solve(long n) {
		ISolver solver = SolverFactory.newDefault();

		try {
			solver.addAllClauses(getClauses());
		} catch (ContradictionException e) {
			return Collections.emptyList();
		}

		ISolver iterator = new ModelIterator(solver, n);

		try {
			List<Set<String>> models = new ArrayList<>();
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
		return (generator.getHighestId() - 1) + " " + clauses.size();
	}

	private static boolean filter(String e) {
		return e.startsWith(":") && !e.equals(":true") && !e.equals(":false");
	}

	public void printModelTo(PrintStream out) {
		printModelsTo(out, 1);
	}
}
