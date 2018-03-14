package it.unibz.stud_inf.ils.white.prisma.grounder.parser;

import it.unibz.stud_inf.ils.white.prisma.grounder.Expression;
import it.unibz.stud_inf.ils.white.prisma.grounder.Formula;
import it.unibz.stud_inf.ils.white.prisma.grounder.Substitution;
import it.unibz.stud_inf.ils.white.prisma.grounder.TseitinTransformator;
import it.unibz.stud_inf.ils.white.prisma.solver.Solver;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import java.util.Collections;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

class ParserTest {
	@ParameterizedTest
	@ValueSource(strings = { "(forall @X in { a, b } (\n  @X |\n  (exists #Y in [1 ... 3] t(#Y))))" })
	void parse(String formula) {
		Formula f = Parser.parse(formula);
	}

	@Test
	void transformFoo() {
		Formula f = Parser.parse("forall #X in [1...3] p(#X)");

		TseitinTransformator transformator = new TseitinTransformator();

		transformator.visit(f.ground());

		for (Map.Entry<Expression, Integer> entry : transformator.fmVars.entrySet()) {
			System.out.println(entry.getValue() + "\t-> " + entry.getKey());
		}

		for (Set<Integer> clause : transformator.clauses) {
			System.out.println(clause.stream().map(String::valueOf).collect(Collectors.joining(" ")));
		}
	}

	@Test
	void solveFoo() {
		Formula f = Parser.parse("p | q");
		Solver.solve(f.get(0));

		f = Parser.parse("p & q");
		Solver.solve(f.get(0));
	}

	@Test
	void solveContradiction() {
		Formula f = Parser.parse("p & ~p");
		Solver.solve(f.get(0));
	}

	@Test
	void parseFoo() {
		Formula f = Parser.parse("forall #X in [1...3] p(#X)");
		for (Expression e : f) {
			System.out.println(e.ground(new Substitution()));
		}
	}

	@Test
	void parseBar() {
		Formula f = Parser.parse("exists #X in [1...3] p(#X)");
		for (Expression e : f) {
			System.out.println(e.ground(new Substitution()));
		}
	}

	@Test
	void parseBaXYr() {
		Formula f = Parser.parse("forall #Y in [1...3] exists #X in [1...3] p(#Y,#X,#Y+#X)");
		for (Expression e : f) {
			System.out.println(e.ground(new Substitution()));
		}
	}

	@Test
	void parseBaXr() {
		Formula f = Parser.parse("forall $Y in {a,b,c} exists #X in [1...3] p($Y,#X)");
		for (Expression e : f) {
			System.out.println(e.ground(new Substitution()));
		}
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
	void parseSudoku() {
		Formula f = Parser.parse("/* Encoding of Sudoku problem\n" +
			"\n" +
			"\tvariable v(i,j,d) true iff the cell in row i, column j contains the digit d\n" +
			"\n" +
			"*/\n" +
			"\n" +
			"// every cell contains a digit\n" +
			"\n" +
			"(forall #i in [0...9]\n" +
			"\t(forall #j in [0...9]\n" +
			"\t\t(exists #d in [0...9] v(#i, #j,#d))\n" +
			"\t)\n" +
			")\n" +
			"\n" +
			"// every cell contains only a digit\n" +
			"(forall #i in [0...9]\n" +
			"\t(forall #j in [0...9]\n" +
			"\t\t(forall #d in [0...8]\n" +
			"\t\t\t(forall #d1 in [#d+1...9] (~v(#i,#j,#d) | ~v(#i,#j,#d1))\n" +
			"\t\t\t)\n" +
			"\t\t)\n" +
			"\t)\n" +
			")\n" +
			"\n" +
			"// every row contains each digit once\n" +
			"(forall #i in [0...9]\n" +
			"\t(forall #d in [0...9]\n" +
			"\t\t(forall #j in [0...8]\n" +
			"\t\t\t(forall #j1 in [#j+1...9] (~v(#i,#j,#d) | ~v(#i,#j1,#d))\n" +
			"\t\t\t)\n" +
			"\t\t)\n" +
			"\t)\n" +
			")\n" +
			"\n" +
			"// every column contains each digit once\n" +
			"(forall #j in [0...9]\n" +
			"\t(forall #d in [0...9]\n" +
			"\t\t(forall #i in [0...8]\n" +
			"\t\t\t(forall #i1 in [#i+1...9] (~v(#i,#j,#d) | ~v(#i1,#j,#d))\n" +
			"\t\t\t)\n" +
			"\t\t)\n" +
			"\t)\n" +
			")\n" +
			"\n" +
			"// each 3x3 square contains each digit once\n" +
			"(forall #d in [0...9]\n" +
			"\t(forall #ro in [0...3]\n" +
			"\t\t(forall #co in [0...3]\n" +
			"\t\t\t(forall #i in [0...8]\n" +
			"\t\t\t\t(forall #i1 in [#i+1...9]\n" +
			"\t\t\t\t\t(~v((3*#ro + #i/3), (3*#co+#i%3), d) | ~v((3*#ro + #i1/3), (3*#co+#i1%3), d))\n" +
			"\t\t\t\t)\n" +
			"\t\t\t)\n" +
			"\t\t)\n" +
			"\t)\n" +
			")\n" +
			"\n" +
			"// partial assignment\n" +
			"\n" +
			"( v(1,9,9) & v(3,2,6) & v(3,7,2) & v(6,9,3) & v(8,4,1) & v(8,5,9) & v(8,6,5) & v(9,5,7) )"
		);

		for (Expression e : f) {
			//System.out.println(e);
			System.out.println(e.ground(new Substitution()));
		}
	}
}