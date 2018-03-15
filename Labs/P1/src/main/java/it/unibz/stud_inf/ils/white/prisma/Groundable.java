package it.unibz.stud_inf.ils.white.prisma;

public interface Groundable<T,S> extends Standardizable<S> {
	T ground(Substitution substitution);

	default T ground() {
		return ground(new Substitution());
	}
}
