package it.unibz.stud_inf.ils.white.prisma;

import it.unibz.stud_inf.ils.white.prisma.ast.Atom;
import it.unibz.stud_inf.ils.white.prisma.ast.Expression;
import it.unibz.stud_inf.ils.white.prisma.ast.Formula;
import it.unibz.stud_inf.ils.white.prisma.ast.IntNumberExpression;
import it.unibz.stud_inf.ils.white.prisma.parser.Parser;
import org.antlr.v4.runtime.CharStreams;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import java.io.IOException;
import java.util.Arrays;
import java.util.Collections;
import java.util.Set;

import static it.unibz.stud_inf.ils.white.prisma.Util.SET_COLLECTOR;

class Tests {
	@ParameterizedTest
	@ValueSource(strings = { "(forall @X in { a, b } (\n  @X |\n  (exists #Y in [1 ... 3] t(#Y))))" })
	void parse(String formula) {
		Formula f = Parser.parse(formula);
	}

	@ParameterizedTest
	@ValueSource(strings = {
		"p | q",
		"p & q",
		"p ^ q",
		"p & ~p",
		"~q",
		"~~~~q",
		"p => q",
		"p <=> q",
		"~(~(~p & ~q) & ~(~q & r))",
		"p ? q : r",
		"p <= q",
		"~(p => q)",
		"~(p => s => (q & r))",
		"true & false",
	})
	void solveGround(String formula) {
		Formula f = Parser.parse(formula);
		System.out.println("f:" + f);
		Expression ground = f.ground();
		CNF cnf = ground.initialize();
		System.out.println("c:" + cnf.getStats());
		cnf.printTo(System.out);
		System.out.println("m:" + models(f));
	}

	@ParameterizedTest
	@ValueSource(strings = {
		"forall $x in {a,b} exists $y in {$x,c} p($x,$y)",
		"forall #X in [1...3] p(#X)",
		"forall #X in [1...3] forall #Y in [1...3] p(#X,#Y)",
		"forall #Y in [1...3] exists #X in [1...3] p(#Y,#X,#Y+#X)",
		"exists #X in [1...3] p(#X)",
		"forall $Y in {a,b,c} exists #X in [1...3] p($Y,#X)",
		"forall $X in {a,b} exists $Y in {c,d} forall $Z in {e,f} (p($X) | p($Y) | p($Z))",
		"forall $X in {a,b} exists $Y in {c,d} p($X,$Y)"
	})
	void solveQuantified(String formula) {
		Formula f = Parser.parse(formula);
		System.out.println("f:" + f);
		Expression ground = f.ground();
		System.out.println("g:" + ground);
		CNF cnf = ground.initialize();
		System.out.println("c:" + cnf.getStats());
		cnf.printTo(System.out);
		System.out.println("m:" + models(f));
	}

	private static String models(Formula f) {
		return f.models(Long.MAX_VALUE)
			.stream()
			.map(
				m -> m.stream().map(Object::toString).collect(SET_COLLECTOR)
			)
			.collect(SET_COLLECTOR);
	}

	private static String model(Formula f) {
		return f.model().stream().map(Object::toString).collect(SET_COLLECTOR);
	}

	@Test
	void parseExplosion() {
		for (int n = 1; n < 8; n++) {
			String in = String.join(" ^ ", Collections.nCopies(n, "p"));
			String out = Parser.parse(in).ground().toString();
			System.out.println(n + " " + in.length() + " " + out.length());

			if (out.length() < 80) {
				System.out.println(out);
			}
		}
	}

	@Test
	void sudoku() throws IOException {
		Formula f = Parser.parse(CharStreams.fromStream(this.getClass().getResourceAsStream("/sudoku.bool")));

		int[][] solution = new int[9][9];

		CNF cnf = f.ground().initialize();

		System.out.println(cnf.getStats());

		Set<Atom> model = cnf.model();

		for (Atom a : model) {
			int row = ((IntNumberExpression)a.getArgs().get(0)).toInteger();
			int col = ((IntNumberExpression)a.getArgs().get(1)).toInteger();
			int val = ((IntNumberExpression)a.getArgs().get(2)).toInteger();

			solution[row][col] = val + 1;
		}

		for (int[] row : solution) {
			System.out.println(Arrays.toString(row));
		}
	}
}