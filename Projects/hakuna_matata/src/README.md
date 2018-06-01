# Hakuna Matata

A playing agent for "Hunt the Wumpus".

## Usage

  + `-size` allows to set the size of the generated world, as a positive integer number.
  + `-seed` allows to set the seed for the world generator, as a hexadecimal number.
  + `-world` allows to set the world specification (size, location of pits/wumpus/gold), given as an input file.
  + `-agent` allows to specify a playing agent for the current game. Possible values are: `proxy`, `perfect`, `asp`.
  + `-generate` allows to generate a world together with the score obtained by the perfect agent over it, given a base.
  + `-benchmark` allows to test an agent against a given benchmark suite.

## Embedding inside the Wumpus World Simulator

The [Wumpus World Simulator](https://gitlab.inf.unibz.it/ILS/wumpus-world-simulator) is available via
a [Git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules) at `src/wsu`. To check out the
contents, run the following commands:

    $ git submodule init
    Submodule 'Projects/wumpus/wsu' (git@gitlab.inf.unibz.it:ILS/wumpus-world-simulator.git) registered for path 'src/wsu'
    $ git submodule update
    Cloning into '/tmp/white/Projects/wumpus/src/wsu'...
    Submodule path 'src/wsu': checked out 'ca54e7cbf449134d45363c84820575cf401f950c'

Next, navigate to the directory:

    $ cd src/wsu

Make sure that your Python configuration is set up correctly and/or the contents of
`Makefile` are alright and go ahead to build `pywumpsim`:

    $ make pywumpsim
    # or
    $ PYTHON_CONFIG=python-config3 make pywumpsim

To invoke the simulator correctly, make sure that `PYTHONPATH` points at `src`, i.e.:

    $ PYTHONPATH=.. ./pywumpsim

Of course, it also works the other way round:

    $ cd ..
    $ PYTHONPATH=. ./wsu/pywumpsim

Generally, you may well be able to use a precompiled `pywumpsim` binary. Just point
`PYTHONPATH` at `src`, which is where `PyAgent.py` is located.
