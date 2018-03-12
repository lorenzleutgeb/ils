package it.unibz.stud_inf.ils.white.prisma.grounder;

public class Variable extends Expression {
	private final String raw;

	public Variable(String raw) {
		this.raw = raw;
	}

	@Override
	public String toString() {
		return "_" + raw;
	}
}
