package it.unibz.stud_inf.ils.white.prisma;

@FunctionalInterface
public interface Groundable<T> {
	T ground(Substitution substitution);

	default T ground() {
		return ground(new Substitution());
	}
}
