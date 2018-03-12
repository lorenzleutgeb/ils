package it.unibz.stud_inf.ils.white.prisma.grounder.parser;

import it.unibz.stud_inf.ils.white.prisma.grounder.Formula;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.*;
import org.junit.jupiter.params.provider.ValueSource;
import org.junit.platform.engine.support.descriptor.ClasspathResourceSource;

import static org.junit.jupiter.api.Assertions.*;

class ParserTest {
	@ParameterizedTest
	@ValueSource(strings = { "(forall _x in { a, b } (\n  _x |\n  (exists _y in {1 .. 3} t(_y))))" })
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
			"(forall _i in {0..9}\n" +
			"\t(forall _j in {0..9}\n" +
			"\t\t(exists _d in {0..9} v(_i,_j,_d))\n" +
			"\t)\n" +
			")\n" +
			"\n" +
			"// every cell contains only a digit\n" +
			"(forall _i in {0..9}\n" +
			"\t(forall _j in {0..9}\n" +
			"\t\t(forall _d in {0..8}\n" +
			"\t\t\t(forall _d1 in {_d+1..9} (~v(_i,_j,_d) | ~v(_i,_j,_d1))\n" +
			"\t\t\t)\n" +
			"\t\t)\n" +
			"\t)\n" +
			")\n" +
			"\n" +
			"// every row contains each digit once\n" +
			"(forall _i in {0..9}\n" +
			"\t(forall _d in {0..9}\n" +
			"\t\t(forall _j in {0..8}\n" +
			"\t\t\t(forall _j1 in {_j+1..9} (~v(_i,_j,_d) | ~v(_i,_j1,_d1))\n" +
			"\t\t\t)\n" +
			"\t\t)\n" +
			"\t)\n" +
			")\n" +
			"\n" +
			"// every column contains each digit once\n" +
			"(forall _j in {0..9}\n" +
			"\t(forall _d in {0..9}\n" +
			"\t\t(forall _i in {0..8}\n" +
			"\t\t\t(forall _i1 in {_i+1..9} (~v(_i,_j,_d) | ~v(_i1,_j,_d1))\n" +
			"\t\t\t)\n" +
			"\t\t)\n" +
			"\t)\n" +
			")\n" +
			"\n" +
			"// each 3x3 square contains each digit once\n" +
			"(forall _d in {0..9}\n" +
			"\t(forall _ro in {0..3}\n" +
			"\t\t(forall _co in {0..3}\n" +
			"\t\t\t(forall _i in {0..8}\n" +
			"\t\t\t\t(forall _i1 in {_i+1..9}\n" +
			"\t\t\t\t\t(~v((3*_ro + _i/3), (3*_co+_i%3), d) | ~v((3*_ro + _i1/3), (3*_co+_i1%3), d))\n" +
			"\t\t\t\t)\n" +
			"\t\t\t)\n" +
			"\t\t)\n" +
			"\t)\n" +
			")\n" +
			"\n" +
			"// partial assignment\n" +
			"\n" +
			"( v(1,9,9) & v(3,2,6) & v(3,7,2) & v(6,9,3) & v(8,4,1) & v(8,5,9) & v(8,6,5) & v(9,5,7) )");
	}
}