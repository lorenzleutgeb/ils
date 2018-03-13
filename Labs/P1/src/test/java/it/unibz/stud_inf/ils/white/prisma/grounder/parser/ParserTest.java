package it.unibz.stud_inf.ils.white.prisma.grounder.parser;

import it.unibz.stud_inf.ils.white.prisma.grounder.Formula;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

class ParserTest {
	@ParameterizedTest
	@ValueSource(strings = { "(forall @X in { a, b } (\n  @X |\n  (exists $Y in [1 ... 3] t($Y))))" })
	void parse(String formula) {
		Formula f = Parser.parse(formula);
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
			"(forall $i in [0...9]\n" +
			"\t(forall $j in [0...9]\n" +
			"\t\t(exists $d in [0...9] v($i, $j,$d))\n" +
			"\t)\n" +
			")\n" +
			"\n" +
			"// every cell contains only a digit\n" +
			"(forall $i in [0...9]\n" +
			"\t(forall $j in [0...9]\n" +
			"\t\t(forall $d in [0...8]\n" +
			"\t\t\t(forall $d1 in [$d+1...9] (~v($i,$j,$d) | ~v($i,$j,$d1))\n" +
			"\t\t\t)\n" +
			"\t\t)\n" +
			"\t)\n" +
			")\n" +
			"\n" +
			"// every row contains each digit once\n" +
			"(forall $i in [0...9]\n" +
			"\t(forall $d in [0...9]\n" +
			"\t\t(forall $j in [0...8]\n" +
			"\t\t\t(forall $j1 in [$j+1...9] (~v($i,$j,$d) | ~v($i,$j1,$d1))\n" +
			"\t\t\t)\n" +
			"\t\t)\n" +
			"\t)\n" +
			")\n" +
			"\n" +
			"// every column contains each digit once\n" +
			"(forall $j in [0...9]\n" +
			"\t(forall $d in [0...9]\n" +
			"\t\t(forall $i in [0...8]\n" +
			"\t\t\t(forall $i1 in [$i+1...9] (~v($i,$j,$d) | ~v($i1,$j,$d1))\n" +
			"\t\t\t)\n" +
			"\t\t)\n" +
			"\t)\n" +
			")\n" +
			"\n" +
			"// each 3x3 square contains each digit once\n" +
			"(forall $d in [0...9]\n" +
			"\t(forall $ro in [0...3]\n" +
			"\t\t(forall $co in [0...3]\n" +
			"\t\t\t(forall $i in [0...8]\n" +
			"\t\t\t\t(forall $i1 in [$i+1...9]\n" +
			"\t\t\t\t\t(~v((3*$ro + $i/3), (3*$co+$i%3), d) | ~v((3*$ro + $i1/3), (3*$co+$i1%3), d))\n" +
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
	}
}