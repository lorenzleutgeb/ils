# Hakuna Matata the Wumpus Hunter

This is an implementation of an agent that plays "Hunt the Wumpus".

Input should be given as follows:

| Predicate | Terms  | Semantics |
|-----------|--------|-----------|
| now       |  X Y O | The agent is currently at position X, Y and its orientation is O. |
| stench    |  X Y   | The agent has perceived a stench at position X, Y. |
| breeze    |  X Y   | The agent has perceived a breeze at position X, Y. |
| glitter   |  X Y   | The agent has perceived a glitter at position X, Y. |
| explored  |  X Y   | The agent has been or is at position X, Y. |
| bumped    |  X Y   | The agent has bumped against a wall when it attempted to move to X, Y. |
| grabbed   |  X Y   | The agent has performed the grab action at X, Y. |
| shot      |  X Y O | The agent has shot its arrow at X, Y in orientation O. |
| killed    |        | The wumpus has been killed. |

	#maxint = 1000.

## Constants

We use constants to encode concrete orientations, actions and modes, and one
corresponding predicate to represent all of them respectively.

According to `wumpus.common.Orientation` and `.../wsu/Orientation.py`
we define orientations.

	#const right = 0.
	#const up    = 1.
	#const left  = 2.
	#const down  = 3.

	isOrientation 0..3

According to `wumpus.common.Action` and `.../wsu/Action.py`
we define actions.

	#const goforward = 0.
	#const turnleft  = 1.
	#const turnright = 2.
	#const grab      = 3.
	#const shoot     = 4.
	#const climb     = 5.

	isAction 0..5

According to `wumpus.agent.Mode` (not present in `.../wsu`)
we define modes.

	#const explore = 0.
	#const escape  = 1.
	#const kill    = 2.

	isMode 0..3

Additionally we designate two orthogonal orientations as axes.

	axis right
	axis up

Being able to mirror orientations/turns will come in handy.

	mirror         left right
	mirror         up   down

And of course, our mirror is symmetric :)

	mirror         O2   O1
		mirror O1   O2

## World Size

If the agent never bumped against a wall, it has no information
about the size of the world.

	sizeKnown
		bumped _ _

We will therefore derive the size of the world from something
already known. We derive the maximum coordinate we have seen
from the explored rooms we know about.

	exploredSize     X
		explored X Y

	exploredSize       Y
		explored X Y

Since any room we already explored certainly is
part of the world, we can use this information and guess that
the world is "just a little" bigger than we already know.

	size                            S
		not sizeKnown
		#succ             Sm    S
		#max              Sm Se
			exploredSize Se

Of course, if the agent bumped, the size can be directly inferred.

	size               S
		bumped  Sm Y
		>     Sm Y
		#prec Sm   S

	size               S
		bumped  X Sm
		<=    X Sm
		#prec   Sm S

## Rooms, Neighbors, Facing and Bumps

Span the space of rooms.

	room         X Y
		#int X
		#int   Y
		>      Y 0
		>    X   0
		<=     Y S
		<=   X   S
		size     S

	corner 1 1

	corner       X 1
		room X 1
		size X
		sizeKnown

	corner       1 Y
		room 1 Y
		size   Y
		sizeKnown

	corner       S S
		room S S
		size S
		sizeKnown

Two rooms are different if any of the components  X, Y are unequal.

	diff         X1 Y1 X2 Y2
		room X1 Y1
		room       X2 Y2
		!=   X1    X2

	diff         X1 Y1 X2 Y2
		room X1 Y1
		room       X2 Y2
		!=      Y1    Y2

### Distances and Costs

The two predicates `outgoing/2` and `incoming/2` will help us to
keep the space for which we have to compute costs small.

	neighborhood              X2 Y2
		now         X1 Y1       _
		anyNeighbor X1 Y1 X2 Y2
		safe              X2 Y2

	outgoing             X Y
		neighborhood X Y

	outgoing     X Y
		now  X Y _

	incoming     X Y
		safe X Y

We define distance along axes

	distAlong        X1 Y1 X2 Y2 right D
		room     X1 Y1
		room           X2 Y2
		#absdiff       X1 X2       D

	distAlong        X1 Y1 X2 Y2 up D
		#absdiff       Y1 Y2    D
		room     X1 Y1
		room           X2 Y2

And using that, manhattan/taxicab distance is a charm.

	manhattan         X1 Y1 X2 Y2             M
		outgoing  X1 Y1
		distAlong X1 Y1 X2 Y2 right D1
		distAlong X1 Y1 X2 Y2 up       D2
		+                           D1 D2 M

The turn predicate associates two orientations with the action
that must be taken in order to turn from the first orientation
to the second (if possible).

	turn up    left  turnleft
	turn left  down  turnleft
	turn down  right turnleft
	turn right up    turnleft

	turn up    right turnright
	turn down  left  turnright
	turn left  up    turnright
	turn right down  turnright

From here, we abstract towards a cost function. We are
interested in the number of turns that need to be performed
in order to change from one orientation to another.

Of course, no change in orientation is free.

	turns                 O O 0
		isOrientation O

Left and right turns, i.e. ones that do not mirror
orientation take exactly one turn.

	turns                     O1 O2 1
		    isOrientation O1
		    isOrientation    O2
		    !=            O1 O2
		not mirror        O1 O2

The worst case is when the orientations are mirrored.

	turns                  O1 O2 2
		isOrientation  O1
		isOrientation     O2
		mirror         O1 O2

With this simple counts for turns we go further and
compute how many turns are needed along the way from
one room to another.

Again, staying in the same room is free.

	turnsTo               X Y O X Y 0
		outgoing      X Y
		isOrientation     O

Rooms that are faced also need no turns, one can just
go straight forward.

	turnsTo               X1 Y1 O1 X2 Y2 0
		isOrientation       O1
		facing        X1 Y1 _  X2 Y2
		diff          X1 Y1    X2 Y2

All other cases require at most one turn since two
components are off.

	turnsTo               X1 Y1 O1 X2 Y2 1
		outgoing      X1 Y1
		isOrientation       O1
		incoming               X2 Y2
		not turnsTo   X1 Y1 O1 X2 Y2 0

	turnsFrom                X1 Y1 O1 X2 Y2    C
		outgoing         X1 Y1
		isOrientation          O1
		incoming                  X2 Y2
		#min                               C Cm
			reach    X1 Y1    X2 Y2 O2
			turns          O1       O2   Cm

	turnCost              X1 Y1 O1 X2 Y2       C
		outgoing      X1 Y1
		isOrientation       O1
		incoming               X2 Y2
		turnsTo       X1 Y1 O1 X2 Y2 Cp
		turnsFrom     X1 Y1 O1 X2 Y2    Cd
		+                            Cp Cd C

We combine turn cost and Manhattan distance as high level
cost function.

	cost                      X1 Y1 O1 X2 Y2       C3
		outgoing          X1 Y1
		isOrientation           O1
		incoming                   X2 Y2
		turnCost          X1 Y1 O1 X2 Y2 C1
		manhattan         X1 Y1    X2 Y2    C2
		+                                C1 C2 C3

Neighboring rooms along the horizontal and vertical axis.

	neighbor      X1 Y X2 Y right
		room  X1 Y
		room       X2 Y
		#succ X1   X2

	neighbor      X Y1 X Y2 up
		room  X Y1
		room       X Y2
		#succ   Y1   Y2

	neighbor         X1 Y1 X2 Y2 O2
		neighbor X2 Y2 X1 Y1 O1
		mirror               O1 O2

	anyNeighbor           X1 Y1 X2 Y2
		neighbor      X1 Y1 X2 Y2 O
		isOrientation             O

	twoNeighbors        X1 Y1 X2 Y2 X3 Y3
		anyNeighbor X1 Y1 X2 Y2
		anyNeighbor X1 Y1       X3 Y3
		diff              X2 Y2 X3 Y3

	square               X1 Y1 X2 Y2 X3 Y3 X4 Y4
		twoNeighbors X1 Y1 X2 Y2 X3 Y3
		twoNeighbors X4 Y4 X2 Y2 X3 Y3
		diff         X1 Y1             X4 Y4

	triple           X1 Y1 X2 Y2 X3 Y3
		neighbor X1 Y1 X2 Y2       A
		neighbor       X2 Y2 X3 Y3 A
		diff     X1 Y1       X3 Y3
		axis                       A

Rooms that agree on one component.

	facing       X Z up X Y
		room X Z
		<      Z      Y
		room X        Y

	facing       Z Y right X Y
		room           X Y
		<    Z         X
		room Z           Y

	facing         X2 Y2    O2 X1 Y1
		facing X1 Y1 O1    X2 Y2
		mirror       O1 O2

	reach        X1 Y1 X2 Y2 right
		room X1 Y1
		room       X2 Y2
		<    X1    X2

	reach        X1 Y1 X2 Y2 up
		room X1 Y1
		room       X2 Y2
		<       Y1    Y2

	reach        X1 Y1 X2 Y2 left
		room X1 Y1
		room       X2 Y2
		>    X1    X2

	reach        X1 Y1 X2 Y2 down
		room X1 Y1
		room       X2 Y2
		>       Y1    Y2

Complete information about information. We only do this here and
not in Python since we might have assumed a size.

	-explored            X Y
		room         X Y
		not explored X Y

## Do

	priority
		shouldShoot

	priority
		shouldClimb

	priority
		shouldGrab

	priority
		shouldAim

	do shoot
		shouldShoot

	do grab
		shouldGrab

	do climb
		shouldClimb

	do              A
		succAim A

	do                   A
		    towards  A
		not priority

	shouldShoot
		mode   kill
		now    X Y O
		attack X Y O

We restrict ourselves to only grab once.

	-canGrab
		grabbed _ _

	canGrab
		not -canGrab


Pick gold if there's some in the room, independently of the current mode.

	shouldGrab
		now     X Y O
		glitter X Y
		canGrab

Climb if gold is picked and back to initial room.

	shouldClimb
		now 1 1 O
		mode escape

Generally we will be turning and go forward towards a goal. Exceptions are when we
want to take high priority actions like grabbing, climbing or shooting.

	canFace                          A
		facing X1 Y1    O2 X2 Y2
		now    X1 Y1 O1
		next               X2 Y2
		!=           O1 O2
		turn         O1 O2       A

	-cannotFace
		isAction A
		canFace  A

	cannotFace
		not -cannotFace

	towards goforward
		facing X1 Y1 O1 X2 Y2
		now    X1 Y1 O1
		next            X2 Y2

	towards         A
		canFace A
		not towards goforward

If the agent cannot go forward towards next and also cannot
face it by turning once it needs to turn around. We currently
implement this as left turns always. There might be better
ways to sort this out...

	towards turnleft
		not towards goforward
		cannotFace

## Detection Of Wumpus

	wumpus            X1 Y1
		 square   X1 Y1 X2 Y2 X3 Y3 X4 Y4
		 stench         X2 Y2
		 stench               X3 Y3
		 explored                   X4 Y4
		-killed

Antipodal matching.

	wumpus                X2 Y2
		 triple X1 Y1 X2 Y2 X3 Y3
		 stench X1 Y1
		 stench             X3 Y3
		-killed

Corner case.

	wumpus                      XW YW
		 twoNeighbors XC YC XW YW XE YE
		 stench       XC YC
		 corner       XC YC
		 explored                 XE YE
		-killed

Auxiliary flag to signal detection of wumpus.

	wumpusDetected
		room   X Y
		wumpus X Y

If wumpus is not certainly detected, we must exclude other rooms where it might be.

	possibleWumpus                X2 Y2
		    anyNeighbor X1 Y1 X2 Y2
		    -explored         X2 Y2
		    stench      X1 Y1
		not shotAt            X2 Y2
		    -killed
		not wumpusDetected

	shotAt                  X Y
		facing XS YS OS X Y
		shot   XS YS OS

## Detection Of Pits

A neighbor of a breeze is a possible pit if it can be.

	possiblePit         XB YB XP YP
		breeze      XB YB
		anyNeighbor XB YB XP YP
		not -pit          XP YP

Any explored room certainly cannot be a pit, otherwise we would be dead by now.

	-pit             X Y
		explored X Y

If we have explored a room already and felt no brezee, then no neighbor can be a pit.

	-pit                      X2 Y2
		anyNeighbor X1 Y1 X2 Y2
		-breeze     X1 Y1

Finally, we assume that there are pits where there might be possible pits.

	pit                     X Y
		possiblePit _ _ X Y

## Safety Of Rooms

Any room where the wumpus is is not safe.

	safe             X Y
		explored X Y

	-safe          X Y
		wumpus X Y

	-safe                  X Y
		possibleWumpus X Y

	-safe       X Y
		pit X Y

	safe                   X Y
		     reachable X Y
		not -safe      X Y

## Explore Mode

	reachable           X Y
		anyNeighbor X Y XE YE
		explored        XE YE

	reachable        X Y
		explored X Y

Auxiliary flag to signal whether we can still explore further.

	frontier           X Y
		 reachable X Y
		 safe      X Y
		-explored  X Y

	shouldExplore
		frontier X Y

## Kill Mode

This mode is concerned with killing, or trying to kill, the wumpus.
Killing the wumpus makes sense if this allows to further explore
the world.
Trying to kill it may still allow us to infer where the wumpus is,
even though it might still be alive.

First, we identify cases where we certainly should not (attempt to)
kill the wumpus.

If the wumpus is in a room where there might also be a pit, then
we will not be able to pass safely even if we manage to kill it.

	dontShoot
		wumpus X Y
		pit    X Y

The same holds for uncertainty of the wumpus' location. Note
that this constraint may be relaxed, since in the case we miss
the wumpus, we might deduce that we can pass through another
room.

	dontShoot
		possibleWumpus X Y
		pit            X Y

Certainly, we cannot (and will not) shoot if we already used our
arrow.

	dontShoot
		shot _ _ _

Also, if the wumpus is already killed, we will not shoot again.

	dontShoot
		killed

If we already have the gold, we should be on our way out of the
cave, and leave the wumpus alone.

	dontShoot
		grabbed _ _

We can kill the wumpus if we know where it is, and there is a
safe room from which it can be faced.

	canKill        XS YS OS
		facing XS YS OS XW YW
		wumpus          XW YW
		safe   XS YS

We should actually kill the wumpus if it is possible, and if
none of our special cases above tells us not to.

	shouldKill
		    canKill   _ _ _
		not dontShoot

Analogously, we might *try* to kill it.

	canTryKill       X Y O
		facing   X Y O XC YC
		safe     X Y
		possibleWumpus XC YC

	shouldTryKill
		    canTryKill _ _ _
		not shouldKill
		not dontShoot

We generalize from trying to kill and actually killing to an
attack, which streamlines the actions that need to be done in
both cases.

	attack                X Y O
		canTryKill    X Y O
		shouldTryKill

	attack             X Y O
		canKill    X Y O
		shouldKill

	shouldAttack
		attack _ _ _

	aim                        OS
		    !=           O OS
		    attack XS YS   OS
		not attack XS YS O
		    now    XS YS O

	canAim                  A
		turn      O1 O2 A
		aim          O2
		now   _ _ O1

	-cannotAim
		canAim _

	cannotAim
		not -cannotAim

	succAim        A
		canAim A
		mode   kill

	succAim           turnleft
		aim       _
		cannotAim
		mode      kill

	shouldAim
		succAim A

## A*-Search

This section is concerned with selection of the goal room,
and consequently the next room to move to.

We will use weak constraints in two levels. The first level
is conerned with finding out the optimal goal while the
second level is then about choosing the next room.

	level 1
	level 2

### Candidate Rooms

For both levels we will define candidate sets in the following
subsections.

#### Goal Room

For convenience we define a selection on the cost function that
fixes the current location and orientation of the agent.

	costFromNow           X2 Y2 C
		cost X1 Y1 O1 X2 Y2 C
		now  X1 Y1 O1

Now, for the three modes that require goals, we define candidate
sets.

In the explore mode, interesting candidates are those rooms that
we have not yet explored and for which we know that they are safe.

	candidate 1         X Y C
		costFromNow X Y C
		frontier    X Y
		mode        explore

The goal is a room form which we can attack the wumpus.

	candidate 1         X Y C
		costFromNow X Y C
		attack      X Y _
		mode        kill

When escaping, the only candidate is the starting point.

	candidate 1 1 1 1
		mode escape

#### Next Room

Choosing the next room is trivial if the goal room is
adjacent to the one that the agent is currently in:
Just move there.

	easyGoal
		now         XN YN       _
		anyNeighbor XN YN XG YG
		goal              XG YG

	candidate 2      X Y C
		choice 1 X Y C
		easyGoal

Otherwise, choose an adjacent room.

	candidate 2                      X2 Y2                C
		    now         X1 Y1 O1
		    anyNeighbor X1 Y1    X2 Y2
		    reach       X1 Y1    X2 Y2 O2
		    safe                 X2 Y2
		    cost                 X2 Y2 O2 XG YG    C2
		    goal                          XG YG
		    turnsFrom   X1 Y1 O1 X2 Y2          C1
		    +                                   C1 C2 C
		not easyGoal

### Weak Constraints

Now, any candidate is either our choice or it is not. Span the
search space.

	choice L X Y C | -choice L X Y C
		level     L
		candidate L X Y C

Of course we want to minimize cost.

	~
		level     L
		candidate L X1 Y1 C1
		candidate L          X2 Y2 C2
		choice    L          X2 Y2 C2
		<=                C1       C2

Give more explicit names to the choices.

	next X Y
		choice 2 X Y C

	goal X Y
		choice 1 X Y C

	foundNext
		next _ _

	-
		    foundGoal
		not foundNext

	foundGoal
		goal _ _

	-
		not foundGoal
		not priority

## Autopilot

	-autopilot
		not autopilot

	autopilot
		not priority
		mode explore

	autopilot
		not priority
		mode escape

## Mode Selector

	mode grab
		shouldGrab

	mode explore
		    shouldExplore
		    canGrab
		not mode grab

	mode kill
		    canGrab
		    shouldAttack
		not mode         grab
		not mode         explore

	mode escape
		not mode grab
		not mode explore
		not mode kill

## Consistency

	wouldBump
		now _ 1 down

	wouldBump
		now 1 _ left

	wouldBump
		size S
		now  _ S up

	wouldBump
		size S
		now  S _ right

	inSomeMode
		isMode M
		mode   M

	doingSomething
		isAction A
		do       A

	breezeHasPossiblePit XB YB
		breeze       XB YB
		possiblePit  XB YB _ _

0 We should not go forward, since that would be our second time to bump.

	bad 0
		do goforward
		wouldBump

2 Don't shoot if the wumpus is already dead!

	bad 2
		do shoot
		killed

3 The agent is not ubiquitous.

	bad 3
		now X Y _
		now X Z _
		!=  Y Z

	bad 3
		now X Y _
		now Z Y _
		!=  X Z

4 We cannot be in more than one mode.

	bad 4
		mode X
		mode   Y
		!=   X Y

5 We must be in one mode.

	bad 5
		not inSomeMode

6 We cannot do two things.

	bad 6
		do A1
		do    A2
		!= A1 A2

7 We must do something.

	bad 7
		not doingSomething

8 Wumpus detection must be accurate. There is only one wumpus.

	bad 8
		wumpus X1 Y1
		wumpus       X2 Y1
		!=     X1    X2

	bad 8
		wumpus X1 Y1
		wumpus X1    Y2
		!=        Y1 Y2

10 There is a room outside of the world. Whut?

	bad 10
		room X Y
		>    X   S
		size     S

	bad 10
		room X Y
		>      Y S
		size     S

11 A breeze must have at least one possiblePit.

	bad 11
		breeze                   XB YB
		not breezeHasPossiblePit XB YB

12 explored/2 and notExplored/2 must be disjoint!

	bad 12
		explored    X Y
		notExplored X Y

13 A room cannot be -safe and explored.

	bad 13
		room     X Y
		-safe    X Y
		explored X Y

14 We are in explore mode, have no triggers to climb or shoot, but still did not find a goal.

	bad 14
		not foundGoal
		not shouldGrab
		not shouldClimb
		mode explore

16 Cost function must be decisive.

	bad 16
		cost X Y O X2 Y2 C1
		cost X Y O X2 Y2    C2
		!=               C1 C2

17 Rotation cost must be decisive.

	bad 17
		turnCost X1 Y1 O1 X2 Y2 C1
		turnCost X1 Y1 O1 X2 Y2    C2
		!=                     C1 C2
