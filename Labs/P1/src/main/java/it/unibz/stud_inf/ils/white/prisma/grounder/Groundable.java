package it.unibz.stud_inf.ils.white.prisma.grounder;

@FunctionalInterface
public interface Groundable<T> {
	T ground(Substitution substitution);
}
