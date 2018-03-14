package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.Substitution;

public abstract class Arg {
	public abstract Arg ground(Substitution substitution);
}
