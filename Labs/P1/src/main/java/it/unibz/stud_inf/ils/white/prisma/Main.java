package it.unibz.stud_inf.ils.white.prisma;

import it.unibz.stud_inf.ils.white.prisma.ast.Formula;
import it.unibz.stud_inf.ils.white.prisma.parser.Parser;
import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.CharStreams;
import org.apache.commons.cli.*;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintStream;

public class Main {
	private static final String OPT_MODE = "format";
	private static final String OPT_N = "n";
	private static final String OPT_INPUT = "input";
	private static final String OPT_OUTPUT = "output";
	private static final String DEFAULT_MODE = "solve";

	private enum Mode {
		CNF, DIMACS, SOLVE
	}

	public static void main(String[] args) throws IOException {
		final Options options = new Options();

		Option modeOption = new Option("m", OPT_MODE, true, "mode of operation");
		modeOption.setArgs(1);
		modeOption.setArgName("<cnf|dimacs|solve>");
		modeOption.setRequired(true);
		options.addOption(modeOption);

		Option nOption = new Option("n", OPT_N, true, "number of models to search for (only relevant in mode 'solve', default value 1)");
		nOption.setArgs(1);
		nOption.setArgName("n");
		nOption.setRequired(false);
		nOption.setType(Number.class);
		options.addOption(nOption);

		Option inputOption = new Option("i", OPT_INPUT, true, "name of input file");
		nOption.setArgs(1);
		nOption.setArgName("<file>");
		nOption.setRequired(true);
		options.addOption(inputOption);

		Option outputOption = new Option("o", OPT_OUTPUT, true, "name of output file");
		nOption.setArgs(1);
		nOption.setArgName("<file>");
		nOption.setRequired(true);
		options.addOption(outputOption);

		CommandLine commandLine;
		try {
			commandLine = new DefaultParser().parse(options, args);
		} catch (ParseException e) {
			System.err.println(e.getMessage());
			return;
		}

		int limit = 1;
		try {
			Number n = (Number)commandLine.getParsedOptionValue(OPT_N);
			if (n != null) {
				limit = n.intValue();
			}
		} catch (ParseException e) {
			bailOut("Failed to parse number of models requested.", e);
		}

		final String requestedMode = commandLine.getOptionValue(OPT_MODE, DEFAULT_MODE);

		Mode mode;
		try {
			mode = Mode.valueOf(requestedMode.toUpperCase());
		} catch (IllegalArgumentException e) {
			bailOut("Unknown mode. Choose one of {cnf,dimacs,solve}!", null);
			return;
		}

		CharStream inputStream = CharStreams.fromFileName(commandLine.getOptionValue(OPT_INPUT));
		Formula formula = Parser.parse(inputStream);
		CNF cnf = formula.ground().tseitin();

		try (FileOutputStream fos = new FileOutputStream(commandLine.getOptionValue(OPT_OUTPUT))) {
			PrintStream ps = new PrintStream(fos);

			switch (mode) {
				case CNF:
					cnf.printTo(ps);
					break;
				case DIMACS:
					cnf.printDimacsTo(ps);
					break;
				case SOLVE:
					cnf.printModelsTo(ps, limit);
					break;
			}
		}
	}

	private static void bailOut(String s, Exception e) {
		System.err.println(s);
		if (e != null) {
			e.printStackTrace(System.err);
		}
		// LOGGER.error(format, arguments);
		System.exit(1);
		throw new RuntimeException("Reached fatal error.");
	}
}