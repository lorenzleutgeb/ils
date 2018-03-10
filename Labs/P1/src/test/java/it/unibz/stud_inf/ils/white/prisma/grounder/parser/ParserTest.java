package it.unibz.stud_inf.ils.white.prisma.grounder.parser;

import it.unibz.stud_inf.ils.white.prisma.grounder.Formula;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.*;
import org.junit.jupiter.params.provider.ValueSource;

import static org.junit.jupiter.api.Assertions.*;

class ParserTest {
	@ParameterizedTest
	@ValueSource(strings = { "(forall _x in { a, b } (\n  _x |\n  (exists _y in {1 .. 3} t(_y))))" })
	void parse(String formula) {
		Formula f = Parser.parse(formula);
	}
}