package it.unibz.stud_inf.ils.white.prisma.grounder;

import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;

public class Substitution {
	private Map<Variable, Object> erased;

	public Substitution() {
		this.erased = new HashMap<>();
	}

	/**
	 * Computes the unifier of the atom and the instance and stores it in the variable substitution.
	 * @param atom the body atom to unify
	 * @param instance the ground instance
	 * @param substitution if the atom does not unify, this is left unchanged.
	 * @return true if the atom and the instance unify. False otherwise

	static Substitution unify(Atom atom, Instance<Term> instance, Substitution substitution) {
		for (int i = 0; i < instance.size(); i++) {
			if (instance.getTerm(i) == atom.getTerms().get(i) ||
				substitution.unifyTerms(atom.getTerms().get(i), instance.getTerm(i))) {
				continue;
			}
			return null;
		}
		return substitution;
	}
	 */

	/**
	 * Checks if the left possible non-ground term unifies with the ground term.
	 * @param termNonGround
	 * @param termGround
	 * @return

	public boolean unifyTerms(Term termNonGround, Term termGround) {
		if (termNonGround == termGround) {
			// Both terms are either the same constant or the same variable term
			return true;
		} else if (termNonGround instanceof ConstantTerm) {
			// Since right term is ground, both terms differ
			return false;
		} else if (termNonGround instanceof VariableTerm) {
			VariableTerm variableTerm = (VariableTerm)termNonGround;
			// Left term is variable, bind it to the right term.
			Term bound = eval(variableTerm);

			if (bound != null) {
				// Variable is already bound, return true if binding is the same as the current ground term.
				return termGround == bound;
			}

			terms.put(variableTerm, termGround);
			return true;
		}
		return false;
	}
	 */

	/**
	 * This method should be used to obtain the {@link Term} to be used in place of
	 * a given {@link VariableTerm} under this substitution.
	 *
	 * @param variable the variable term to ground, if possible
	 * @return a constant term if the substitution contains the given variable, {@code null} otherwise.
	 */
	@SuppressWarnings("unchecked")
	public <T> T eval(Variable<T> variable) {
		Object o = erased.get(variable);
		return (T) o;
	}

	@SuppressWarnings("unchecked")
	public <T> T put(Variable<T> variable, T item) {
		return (T) erased.put(variable, item);
	}

	public boolean isEmpty() {
		return erased.isEmpty();
	}
}
