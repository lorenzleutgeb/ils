package it.unibz.stud_inf.ils.white.prisma;

import java.util.stream.Collector;
import java.util.stream.Collectors;

public class Util {
	public static final Collector<CharSequence, ?, String> SET_COLLECTOR = Collectors.joining(", ", "{", "}");
}