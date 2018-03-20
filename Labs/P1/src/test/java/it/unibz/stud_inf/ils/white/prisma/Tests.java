package it.unibz.stud_inf.ils.white.prisma;

import it.unibz.stud_inf.ils.white.prisma.ast.Formula;
import it.unibz.stud_inf.ils.white.prisma.ast.Quantifier;
import it.unibz.stud_inf.ils.white.prisma.parser.Parser;
import org.antlr.v4.runtime.CharStreams;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.junit.jupiter.params.provider.ValueSource;

import java.io.IOException;
import java.util.Collections;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class Tests {
	static Stream<? extends Arguments> groundInstances() {
		return Stream.of(
			Arguments.of("~q",           1, 1, 1),
			Arguments.of("p | q",        2, 1, 3),
			Arguments.of("p & q",        2, 2, 1),
			Arguments.of("p ^ q",        2, 2, 2),
			Arguments.of("p & ~p",       1, 2, 0),
			Arguments.of("~~~~q",        1, 1, 1),
			Arguments.of("p -> q",       2, 1, 3),
			Arguments.of("p <-> q",      2, 2, 2),
			Arguments.of("p ? q : r",    3, 2, 4),
			Arguments.of("p <- q",       2, 1, 3),
			Arguments.of("~(p -> q)",    2, 2, 1),
			Arguments.of("true & false", 1, 2, 0),
			Arguments.of("1 > 2",        1, 2, 0),

			Arguments.of("~(~(~p & ~q) & ~(~q & r))", 3 + 2, 7, 3),
			Arguments.of("~(p -> s -> (q & r))", 4, 2, 9)
		);
	}

	@ParameterizedTest
	@MethodSource("groundInstances")
	void solveGround(String formula, int vars, int clauses, int models) {
		solveAndAssert(formula, vars, clauses, models);
	}

	void solveAndAssert(String formula, int vars, int clauses, int models) {
		final Formula f = Parser.parse(formula);
		final ConjunctiveNormalForm cnf = f.toConjunctiveNormalForm();

		assertEquals(vars, cnf.getVariableCount(), "Number of Variables");
		assertEquals(clauses, cnf.getClauseCount(), "Number of Clauses");
		assertEquals(models, cnf.models().size(), "Number of Models");
	}

	@Test
	public void testQuants() {
		Quantifier.optimizeOrder(Collections.emptyList());
	}

	@ParameterizedTest
	@ValueSource(strings = {"(forall @X in a, b { }"})
	void parse(final String formula) {
		assertThrows(RuntimeException.class, () -> Parser.parse(formula));
	}

	@ParameterizedTest
	@ValueSource(strings = {
		"forall @X in {a,b} ~(@X & (exists #Y in [1...3] (t(#Y) -> q(#Y))))",

		"forall $x in {a,b} exists $y in {$x,c} p($x,$y) # noswitch, fine, related, dependent",
		"exists $x in {a,b} forall $y in {$x,c} p($x,$y) # noswitch, related, dependent",
		"exists $x in {a,b} forall $y in {c,d} p($x,$y) # noswitch, dependent",
		"exists $x in {a,b} forall $y in {c,d} (p($x) & p($y)) # noswitch, fine, related, dependent",

		"exists $y in {a,b,c} forall $x in {a,b,c} (q & (p($x) & p($y)))",
		"forall $x in {a,b,c} exists $y in {a,b,c} (q & (p($x) & p($y)))",

		"exists $y in {a,b,c} forall $x in {a,b,c} (q | (p($x) | p($y)))",
		"forall $x in {a,b,c} exists $y in {a,b,c} (q | (p($x) | p($y)))",

		"forall #X in [1...3] p(#X)",
		"forall #X in [1...3] forall #Y in [1...3] p(#X,#Y)",
		"forall #Y in [1...3] exists #X in [1...3] p(#Y,#X,#Y+#X)",
		"exists #X in [1...3] p(#X)",
		"forall $Y in {a,b,c} exists #X in [1...3] p($Y,#X)",
		"forall $X in {a,b} exists $Y in {c,d} forall $Z in {e,f} (p($X) | p($Y) | p($Z))",
		"forall $X in {a,b} exists $Y in {c,d} p($X,$Y)",
		"forall @X in {a,b} (@X & (exists #Y in [1...3] t(#Y)))",
		"~(exists $X in {a,b} p($X))",
		"(forall $x in {a,b} "+
			"(exists $y in {a,b} "+
				"phi($y)"+
			") | ("+
				"(exists $z in {a,b} psi($z))"+
			" -> "+
				"rho($x)" +
			")" +
		")",
		"forall $x in {a,b} ((exists $y in {a,b} phi($y)) | ((exists $z in {a,b} psi($z)) -> rho($x)))",
		"exists #x in [2...6] (#x < 4 & p(#x))",

		"exists $y in {a,b,c} forall $x in {a,b,c} (p($x) & p($y))",
		"forall $x in {a,b,c} exists $y in {a,b,c} (p($x) & p($y))",
	})
	void solveQuantified(String formula) {
		Formula f = Parser.parse(formula);
		System.out.println("f:" + f);
		System.out.println("n:" + (f = f.normalize()));
		//System.out.println("s:" + (f = f.standardize()));
		System.out.println("p:" + (f = f.pushQuantifiersDown()));
		f = f.ground();
		System.out.println("g:" + (f));
		ConjunctiveNormalForm cnf = f.tseitin();
		System.out.println("c:" + cnf.getStats());
		System.out.println(cnf);
		cnf.printModelsTo(System.out);
	}

	@Test
	void parseExplosion() {
		for (int n = 1; n < 8; n++) {
			String in = String.join(" ^ ", Collections.nCopies(n, "p"));
			String out = Parser.parse(in).toConjunctiveNormalForm().toString();
			System.out.println(n + " " + in.length() + " " + out.length());

			if (out.length() < 80) {
				System.out.println(out);
			}
		}
	}

	static Stream<? extends Arguments> instanceFiles() throws Exception {
		return Stream.of("/sudoku.bool", "/quants-3.bool",  "/quants-5.bool")
			.map(Tests.class::getResourceAsStream)
			.map(Arguments::of);
	}

	@ParameterizedTest
	@ValueSource(strings = {"/sudoku.bool", "/quants-3.bool",  "/quants-5.bool"})
	void instance(String fileName) throws IOException {
		Formula f = Parser.parse(CharStreams.fromStream(getClass().getResourceAsStream(fileName)));
		ConjunctiveNormalForm cnf = f.toConjunctiveNormalForm();
		System.out.println(cnf.getStats());
	}
}
