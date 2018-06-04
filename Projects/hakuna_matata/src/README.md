# Hakuna Matata

A playing agent for "Hunt the Wumpus".

## Dependencies

Besides a Python 3 runtime, the only dependency is the [DLV system](http://www.dlvsystem.com/dlv/).
An executable named `dlv` will be picked up if it is (a) on the `$PATH` or (b) in the current working
directory at the time of executing Hakuna Matata. For example:

    $ which dlv
    ~/bin/dlv
    # Will work!

    $ which dlv
    /usr/bin/which: no dlv in (...)
    # Note that DLV is not in the $PATH!
    $ file dlv
    dlv: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, for GNU/Linux 2.6.15, BuildID[sha1]=9b02b8807051dc70990bda5d9f1744f10eb87675, stripped
    # DLV is in the current working directory, good!
    $ chmod u+x dlv
    # Don't forget to allow exection!

If `dlv` cannot be found in either location, an attempt will be made to download it to the
current working directory, before proceeding to the *Hunt the Wumpus* game. For example:

    $ file dlv
    dlv: cannot open 'dlv' (No such file or directory)
    $ python3 -m hakuna_matata.cli -world '../worlds/test.txt'
    NOTE: Could not find DLV! Will attempt to download it.
    965
    $ file dlv
    dlv: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, for GNU/Linux 2.6.15, BuildID[sha1]=9b02b8807051dc70990bda5d9f1744f10eb87675, stripped

## Usage

  + `-size` allows to set the size of the generated world, as a positive integer number.
  + `-seed` allows to set the seed for the world generator, as a hexadecimal number.
  + `-world` allows to set the world specification (size, location of pits/wumpus/gold), given as an input file.
  + `-human` if you do not want to have Hakuna matata play, but try out the game yourself.
  + `-generate` allows to generate a world together with the score obtained by the perfect agent over it, given a base.
  + `-benchmark` allows to test an agent against a given benchmark suite.

## Embedding in the Wumpus World Simulator

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
