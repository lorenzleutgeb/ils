package it.unibz.stud_inf.ils.white.prisma.ast;

import org.sat4j.ExitCode;
import org.sat4j.maxsat.MinCostDecorator;
import org.sat4j.maxsat.SolverFactory;
import org.sat4j.pb.IPBSolver;
import org.sat4j.specs.ContradictionException;
import org.sat4j.specs.IOptimizationProblem;
import org.sat4j.specs.IProblem;
import org.sat4j.specs.TimeoutException;

import java.util.List;

public class Quantifier<T> {
	private final boolean exists;
	private final Variable<T> variable;
	private final Domain<T> domain;

	public Quantifier(String name, Variable<T> variable, Domain<T> domain) {
		// TODO: Account for UTF-8.
		this.exists = "exists".equals(name.toLowerCase());
		this.variable = variable;
		this.domain = domain;
	}

	private Quantifier(boolean exists, Variable<T> variable, Domain<T> domain) {
		this.exists = exists;
		this.variable = variable;
		this.domain = domain;
	}

	public boolean isExististential() {
		return exists;
	}

	public boolean isUniversal() {
		return exists;
	}

	public Quantifier exists(Variable<T> variable, Domain<T> domain) {
		return new Quantifier<>(true, variable, domain);
	}

	public Quantifier forall(Variable<T> variable, Domain<T> domain) {
		return new Quantifier<>(false, variable, domain);
	}

	public Quantifier flip() {
		return new Quantifier(!exists, variable, domain);
	}

	private boolean dependsOn(Quantifier<T> other) {
		return other.getDomain().getOccuringVariables().contains(variable);
	}

	public Variable<T> getVariable() {
		return variable;
	}

	public Domain<T> getDomain() {
		return domain;
	}

	public MultaryConnectiveExpression.Connective getConnective() {
		return exists ? MultaryConnectiveExpression.Connective.OR : MultaryConnectiveExpression.Connective.AND;
	}

	public Quantifier<T> switchBoth(Variable<T> variable, Domain<T> domain) {
		return new Quantifier<>(exists, variable, domain);
	}

	public static List<Quantifier> optimizeOrder(List<Quantifier> order) {
		// Go from right to left, pulling universal quantifiers as far as possible.
		IPBSolver solver = SolverFactory.newDefault();

		// Generate all "hard" constraints, add them as "exactly".
		//solver.addExactly()

		// Generate all "soft" constraints, add them. How?
		//solver.addAllClauses();

		MinCostDecorator minCost = new MinCostDecorator(SolverFactory.newDefault());
		return null;
	}

	protected static int[] solve(IProblem problem) throws TimeoutException {
		boolean isSatisfiable = false;

		IOptimizationProblem optproblem = (IOptimizationProblem) problem;

		try {
			while (optproblem.admitABetterSolution()) {
				if (!isSatisfiable) {
					if (optproblem.nonOptimalMeansSatisfiable()) {
						// setExitCode(ExitCode.SATISFIABLE);
						if (optproblem.hasNoObjectiveFunction()) {
							return null;
						}
						// log("SATISFIABLE"); //$NON-NLS-1$
					} else if (false) {
						return null;
						// setExitCode(ExitCode.UPPER_BOUND);
					}
					isSatisfiable = true;
					// log("OPTIMIZING..."); //$NON-NLS-1$
				}
				/* log("Got one! Elapsed wall clock time (in seconds):" //$NON-NLS-1$
					+ (System.currentTimeMillis() - getBeginTime())
					/ 1000.0);
				getLogWriter().println(
					CURRENT_OPTIMUM_VALUE_PREFIX
						+ optproblem.getObjectiveValue());
				*/
				optproblem.discardCurrentSolution();
			}
			if (isSatisfiable) {
				return optproblem.model();
				// setExitCode(ExitCode.OPTIMUM_FOUND);
			} else {
				return null;
				// setExitCode(ExitCode.UNSATISFIABLE);
			}
		} catch (ContradictionException ex) {
			assert isSatisfiable;
			// setExitCode(ExitCode.OPTIMUM_FOUND);
		}
		return null;
	}

	@Override
	public String toString() {
		return exists ? "exists" : "forall";
	}
}
