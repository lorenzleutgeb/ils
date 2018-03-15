package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.Standardizable;
import it.unibz.stud_inf.ils.white.prisma.Substitution;

public abstract class Arg<T extends Arg> implements Standardizable<T> {
	public abstract Arg ground(Substitution substitution);
}
