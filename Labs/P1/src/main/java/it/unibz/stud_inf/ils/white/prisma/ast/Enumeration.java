package it.unibz.stud_inf.ils.white.prisma.ast;

import it.unibz.stud_inf.ils.white.prisma.Groundable;
import it.unibz.stud_inf.ils.white.prisma.Substitution;

import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class Enumeration<U extends Groundable<T>, T> extends Domain<T> {
	private final List<U> elements;

	public Enumeration(List<U> elements) {
		this.elements = elements;
	}

	@Override
	public Stream<T> stream(Substitution substitution) {
		return elements.stream().map(p -> p.ground(substitution));
	}

	@Override
	public int size() {
		return elements.size();
	}

	@Override
	public String toString() {
		return elements.stream().map(Object::toString).collect(Collectors.joining(", ", "{", "}"));
	}
}
