package it.unibz.stud_inf.ils.white.prisma.grounder;

import it.unibz.stud_inf.ils.white.prisma.grounder.parser.ConstantTerm;
import it.unibz.stud_inf.ils.white.prisma.grounder.parser.IntVariable;
import it.unibz.stud_inf.ils.white.prisma.grounder.parser.VariableTerm;

import java.util.TreeMap;

public class Substitution {
	private TreeMap<VariableTerm, Term> terms;
	private TreeMap<VariablePredicate, ConstantPredicate> predicates;
	private TreeMap<IntVariable, IntExpression> ints;

	public Substitution() {
		this(new TreeMap<>(), new TreeMap<>(), new TreeMap<>());
	}

	public Substitution(Substitution clone) {
		this(new TreeMap<>(clone.terms), new TreeMap<>(clone.predicates), new TreeMap<>(clone.ints));
	}

	public Substitution(TreeMap<VariableTerm, Term> terms, TreeMap<VariablePredicate, ConstantPredicate> predicates, TreeMap<IntVariable, IntExpression> ints) {
		this.terms = terms;
		this.predicates = predicates;
		this.ints = ints;
	}

	/**
	 * Computes the unifier of the atom and the instance and stores it in the variable substitution.
	 * @param atom the body atom to unify
	 * @param instance the ground instance
	 * @param substitution if the atom does not unify, this is left unchanged.
	 * @return true if the atom and the instance unify. False otherwise
	 */
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

	/**
	 * Checks if the left possible non-ground term unifies with the ground term.
	 * @param termNonGround
	 * @param termGround
	 * @return
	 */
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

	/**
	 * This method should be used to obtain the {@link Term} to be used in place of
	 * a given {@link VariableTerm} under this substitution.
	 *
	 * @param variableTerm the variable term to substitute, if possible
	 * @return a constant term if the substitution contains the given variable, {@code null} otherwise.
	 */
	public Term eval(VariableTerm variableTerm) {
		return this.terms.get(variableTerm);
	}

	public ConstantPredicate eval(VariablePredicate variableTerm) {
		return this.predicates.get(variableTerm);
	}

	public IntExpression eval(IntVariable variableTerm) {
		return this.ints.get(variableTerm);
	}

	public <T extends Comparable<T>> Term put(VariableTerm variableTerm, Term groundTerm) {
		// Note: We're destroying type information here.
		return terms.put(variableTerm, groundTerm);
	}

	public <T extends Comparable<T>> ConstantPredicate put(VariablePredicate variableTerm, ConstantPredicate groundTerm) {
		// Note: We're destroying type information here.
		return predicates.put(variableTerm, groundTerm);
	}

	public boolean isEmpty() {
		return terms.isEmpty() && predicates.isEmpty();
	}
}
