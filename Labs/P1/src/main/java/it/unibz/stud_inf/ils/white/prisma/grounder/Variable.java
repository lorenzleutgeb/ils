package it.unibz.stud_inf.ils.white.prisma.grounder;

public class Variable {
	private final String raw;

	public Variable(String raw) {
		this.raw = raw;
	}

	@Override
	public String toString() {
		return raw;
	}
}
