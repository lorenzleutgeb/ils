# Hakuna Matata

A playing agent for "Hunt the Wumpus".

## Usage

  + `-size` allows to set the size of the generated world, as a positive integer number.
  + `-seed` allows to set the seed for the world generator, as a hexadecimal number.
  + `-world` allows to set the world specification (size, location of pits/wumpus/gold), given as an input file.
  + `-agent` allows to specify a playing agent for the current game. Possible values are: `proxy`, `perfect`, `asp`.
  + `-generate` allows to generate a world together with the score obtained by the perfect agent over it, given a base.
  + `-benchmark` allows to test an agent against a given benchmark suite.
