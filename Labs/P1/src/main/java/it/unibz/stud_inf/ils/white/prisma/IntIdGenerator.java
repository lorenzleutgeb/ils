package it.unibz.stud_inf.ils.white.prisma;

public class IntIdGenerator {
	private int highestId;

	public IntIdGenerator() {
		this(0);
	}

	public IntIdGenerator(int initial) {
		this.highestId = initial;
	}

	public int getNextId() {
		if (highestId == Integer.MAX_VALUE) {
			throw new RuntimeException("Ran out of IDs (integer overflow)");
		}
		return highestId++;
	}

	/**
	 * Resets the internal counter. Useful for resetting before each test.
	 */
	public void resetGenerator() {
		highestId = 0;
	}
}