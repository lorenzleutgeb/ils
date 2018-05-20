    #maxint = 1000.

Knowledge:
now(X,Y,O)   ... The agent is at position X, Y and oriented in direction O,
stench(X,Y)  ... The agent has perceived a stench at position X, Y.
breeze(X,Y)  ...               breeze
glitter(X,Y) ...               glitter
wumpusDead   ... The wumpus is dead.
haveArrow    ... We have an arrow that we may shoot.

## Constants

NOTE: Should correspond to wumpus.common.Orientation
    #const right = 0.
    #const up    = 1.
    #const left  = 2.
    #const down  = 3.

    isOrientation(0..3).

NOTE: Should correspond to wumpus.common.Action
    #const goforward = 0.
    #const turnleft  = 1.
    #const turnright = 2.
    #const grab      = 3.
    #const shoot     = 4.
    #const climb     = 5.

    isAction(0..5).

NOTE: Should correspond to wumpus.agent.Mode
    #const explore = 0.
    #const escape  = 1.
    #const kill    = 2.

    isMode(0..2).

## Basics

We designate two orthogonal orientations as axes.
    axis(right).
    axis(up).

## World Size Detection

    exploredSize(X) :- explored(X,_).
    exploredSize(Y) :- explored(_,Y).

    sizeKnown :- bump(_,_).
    size(S) :- not sizeKnown, Sm = #max{Se: exploredSize(Se)}, S = Sm + 1.
    size(S) :- bump(Sm,Y), Sm > Y, S = Sm - 1.
    size(S) :- bump(X,Sm), Sm > X, S = Sm - 1.

## Cells, Neighbors, Facing And Bumps

Span the space of cells.
    cell(X,Y) :- #int(X), #int(Y), Y > 0, X > 0, Y <= S, X <= S, size(S).

    diff(X1,Y1,X2,Y2) :- X1 != X2, cell(X1,Y1), cell(X2,Y2).
    diff(X1,Y1,X2,Y2) :- Y1 != Y2, cell(X1,Y1), cell(X2,Y2).

    state(X,Y,O) :- cell(X,Y), isOrientation(O).

    distAlong(X1,Y1,X2,Y2,right,D) :- D = X2 - X1, X1 <= X2, cell(X1,Y1), cell(X2,Y2).
    distAlong(X1,Y1,X2,Y2,up,D) :- D = Y2 - Y1, Y1 <= Y2, cell(X1,Y1), cell(X2,Y2).
    distAlong(X2,Y2,X1,Y1,A,D) :- distAlong(X1,Y1,X2,Y2,A,D), axis(A).

    manhattan(X1,Y1,X2,Y2,M) :- distAlong(X1,Y1,X2,Y2,right,D1), distAlong(X1,Y1,X2,Y2,up,D2), M = D1 + D2.

sameRotCost(O1,O2,C) :- O1 <= O2, C = O2 - O1, C < 3, isOrientation(O1), isOrientation(O2).
sameRotCost(0,3,1).
sameRotCost(O2,O1,C) :- rotCost(O1,O2,C).

    mirror(left,right).
    mirror(up,down).

outRotCost(X,Y,O,X,Y,O,0)      :- isOrientation(O), cell(X,Y).
outRotCost(X1,Y1,O,X2,Y2,O,0) :- facing(X1,Y1,O1,X2,Y2), diff(X1,Y1,X2,Y2).
outRotCost(X1,Y1,O1,X2,Y2,O2,1) :- -facing(X1,Y1,O1,X2,Y2), diff(X1,Y1,X2,Y2), rotate(O1,_,O2), facing(X1,Y1,O2,X2,Y2).
outRotCost(X1,Y1,O1,X2,Y2,O2,2) :- -facing(X1,Y1,O1,X2,Y2), diff(X1,Y1,X2,Y2), not rotCost(X1,Y1,O1,X2,Y2,1).

rotCost(X1,Y1,O1,X2,Y2,O2,C) :- sameRotCost()

    cost(X1,Y1,O1,X2,Y2,M) :- state(X1,Y1,O1), cell(X2,Y2), manhattan(X1,Y1,X2,Y2,M).
cost(X1,Y1,O1,X2,Y2,C) :- state(X1,Y1,O1), cell(X2,Y2), manhattan(X1,Y1,X2,Y2,M), rotCost(X1,Y1,O1,X2,Y2,R), C = M + R.

    h(X2,Y2,D) :- now(X1,Y1,O1), cost(X1,Y1,O1,X2,Y2,D).

    rotate(up,turnleft,left).
    rotate(up,turnright,right).
    rotate(down,turnleft,right).
    rotate(down,turnright,left).
    rotate(left,turnleft,down).
    rotate(left,turnright,up).
    rotate(right,turnleft,up).
    rotate(right,turnright,down).

    risk(O) :- now(X,Y,O), neighbor(X,Y,XN,YN,O), -safe(XN,YN).
    -risk(O) :- not risk(O), isOrientation(O).

Neighboring cells along the horizontal and vertical axis.
    neighbor(X1,Y1,X2,Y2,right) :- cell(X1,Y1), cell(X2,Y2), X2 = X1 + 1, Y2 = Y1.
    neighbor(X1,Y1,X2,Y2,up   ) :- cell(X1,Y1), cell(X2,Y2), X2 = X1, Y2 = Y1 + 1.
    neighbor(X1,Y1,X2,Y2,left ) :- cell(X1,Y1), cell(X2,Y2), X2 = X1 - 1, Y2 = Y1.
    neighbor(X1,Y1,X2,Y2,down ) :- cell(X1,Y1), cell(X2,Y2), X2 = X1, Y2 = Y1 - 1.

    anyNeighbor(X1,Y1,X2,Y2) :- neighbor(X1,Y1,X2,Y2,O), isOrientation(O).

    twoNeighbors(X1,Y1,X2,Y2,X3,Y3) :- anyNeighbor(X1,Y1,X2,Y2), anyNeighbor(X1,Y1,X3,Y3), diff(X2,Y2,X3,Y3).

    corner(1,1).
    corner(X,1) :- cell(X,1), sizeKnown, size(X).
    corner(1,Y) :- cell(1,Y), sizeKnown, size(Y).
    corner(S,S) :- cell(S,S), sizeKnown, size(S).

    square(X1,Y1,X2,Y2,X3,Y3,X4,Y4) :- twoNeighbors(X1,Y1,X2,Y2,X3,Y3), twoNeighbors(X4,Y4,X2,Y2,X3,Y3), diff(X1,Y1,X4,Y4).

    triple(X1,Y1,X2,Y2,X3,Y3) :- neighbor(X1,Y1,X2,Y2,A), neighbor(X2,Y2,X3,Y3,A), diff(X1,Y1,X3,Y3), axis(A).

Cells that agree on one component.
    facing(X,Z,up,X,Y) :- cell(X,Y), Z < Y, cell(X,Z).
    facing(X,Z,down,X,Y) :- cell(X,Y), Y < Z, cell(X,Z).
    facing(Z,Y,right,X,Y) :- cell(X,Y), Z < X, cell(Z,Y).
    facing(Z,Y,left,X,Y) :- cell(X,Y), X < Z, cell(Z,Y).

    -facing(X1,Y1,O,X2,Y2) :- not facing(X1,Y1,O,X2,Y2), cell(X1,Y1), isOrientation(O), cell(X2,Y2).

Complete information about information. We only do this here and
not in Python since we might have assumed a size.
    -explored(X,Y) :- cell(X,Y), not explored(X,Y).

## Do

    do(shoot) :- shouldShoot.
    do(grab) :- shouldGrab.
    do(climb) :- shouldClimb.
    do(A) :- succAim(A).
    do(A) :- next(X,Y,_), towards(A), not shouldGrab, not shouldClimb, not shouldShoot, not shouldAim.

    shouldShoot :- mode(kill), now(X,Y,O), attack(X,Y,O).

Pick gold if there's some in the cell, independently of the current mode.
    shouldGrab :- now(X,Y,_), glitter(X,Y).

Climb if gold is picked and back to initial cell.
    shouldClimb :- now(1,1,_), mode(escape).

Generally we will be turning and go forward towards a goal. Exceptions are when we
want to take high priority actions like grabbing, climbing or shooting.

    canFace(A) :- now(X1,Y1,O1), next(X2,Y2,_), facing(X1,Y1,O2,X2,Y2), O1 != O2, rotate(O1,A,O2).
    -cannotFace :- isAction(A), next(X,Y,_), canFace(A).
    cannotFace :- not -cannotFace.

    towards(goforward) :- now(X1,Y1,O1), next(X2,Y2,_), facing(X1,Y1,O1,X2,Y2).
    towards(A) :- not towards(goforward), canFace(A).

TODO: Can we turn in a better way?
    towards(turnleft) :- not towards(goforward), cannotFace.

## Detection Of Wumpus

    wumpus(X1,Y1) :- square(X1,Y1,X2,Y2,X3,Y3,X4,Y4), stench(X2,Y2), stench(X3,Y3), explored(X4,Y4), -wumpusDead.

Antipodal matching.
    wumpus(X2,Y2) :- triple(X1,Y1,X2,Y2,X3,Y3), stench(X1,Y1), stench(X3,Y3), -wumpusDead.

Corner case.
    wumpus(XW,YW) :- stench(XC,YC), corner(XC,YC), twoNeighbors(XC,YC,XW,YW,XE,YE), explored(XE,YE), -wumpusDead.

Auxiliary flag to signal detection of wumpus.
    wumpusDetected :- cell(X,Y), wumpus(X,Y).

If wumpus is not certainly detected, we must exclude other cells where it might be.
    possibleWumpus(X2,Y2) :- anyNeighbor(X1,Y1,X2,Y2), stench(X1,Y1), not wumpusDetected, -explored(X2,Y2), -wumpusDead, not shotAt(X2,Y2).
    shotAt(X,Y) :- shot(XS,YS,OS), facing(XS,YS,OS,X,Y).

## Detection Of Pits

Any explored cell certainly cannot be a pit, otherwise we would be dead by now.
    -pit(X,Y) :- explored(X,Y).

If we have explored a cell already and felt no brezee, then no neighbor can be a pit.
    -pit(X2,Y2) :- -breeze(X1,Y1), anyNeighbor(X1,Y1,X2,Y2).

A neighbor of a breeze is a possible pit if it can be.
    possiblePit(XB,YB,XP,YP) :- breeze(XB,YB), anyNeighbor(XB,YB,XP,YP), not -pit(XP,YP).

## Safety Of Cells

Any cell where the wumpus is is not safe.
    safe(X,Y) :- explored(X,Y).
    -safe(X1,Y1) :- wumpus(X1,Y1).
    -safe(X1,Y1) :- possibleWumpus(X1,Y1).
    -safe(X2,Y2) :- possiblePit(X1,Y1,X2,Y2).

    safe(X,Y) :- cell(X,Y), not -safe(X,Y).

## Explore Mode

    reachable(X,Y) :- explored(XE,YE), anyNeighbor(X,Y,XE,YE).

    toExplore(X,Y) :- reachable(X,Y), safe(X,Y), -explored(X,Y).

Auxiliary flag to signal whether we can still explore further.
    canExplore :- toExplore(_,_).

## Escape Mode

## Kill Mode

    dontShoot :- possibleWumpus(X,Y), possiblePit(_,_,X,Y).
    dontShoot :- wumpus(X,Y), possiblePit(_,_,X,Y).
    dontShoot :- not haveArrow.
    dontShoot :- wumpusDead.

    canKill(XS,YS,OS) :- wumpus(XW,YW), safe(XS,YS), facing(XS,YS,OS,XW,YW).
    shouldKill :- canKill(_,_,_), not dontShoot.

    canTryKill(X,Y,O) :- possibleWumpus(XC,YC), safe(X,Y), facing(X,Y,O,XC,YC).
    shouldTryKill :- not shouldKill, canTryKill(_,_,_), not dontShoot.

    attack(X,Y,O) :- shouldTryKill, canTryKill(X,Y,O).
    attack(X,Y,O) :- shouldKill, canKill(X,Y,O).

    aim(OS) :- attack(XS,YS,OS), now(XS,YS,O), O != OS, not attack(XS,YS,O).

    canAim(A) :- aim(O2), now(_,_,O1), rotate(O1,A,O2).
    -cannotAim :- canAim(A).
    cannotAim :- not -cannotAim.

    succAim(A) :- canAim(A), mode(kill).
    succAim(turnleft) :- aim(_), cannotAim, mode(kill).

    shouldAim :- succAim(_).

Interesting candidates are those cells that we have not yet explored
and we know that they are safe.
    candidate(1,X,Y,C) :- h(X,Y,C), mode(explore), toExplore(X,Y).
    candidate(1,XS,YS,C) :- h(XS,YS,C), attack(XS,YS,OS), mode(kill).
    candidate(2,X,Y,C) :- now(XN,YN,_), cost(X,Y,O,XG,YG,C), anyNeighbor(XN,YN,X,Y), safe(X,Y), isOrientation(O), goal(XG,YG,_).

## Optimization For Goal

    level(1).
    level(2).
    next(X,Y,C) :- choice(2,X,Y,C).
    goal(X,Y,C) :- choice(1,X,Y,C).
    goal(1,1,C) :- h(1,1,C), mode(escape).

    choice(L,X,Y,C) v -choice(L,X,Y,C) :- candidate(L,X,Y,C), level(L).
    :~ candidate(L,_,_,C1), candidate(L,X,Y,C2), C2 > C1, choice(L,X,Y,C2), level(L). [1:1]
    :- candidate(L,X1,_,C), candidate(L,X2,_,C), X2 > X1, choice(L,X2,Y,C), level(L).
    :- candidate(L,X,Y1,C), candidate(L,X,Y2,C), Y2 > Y1, choice(L,X,Y2,C), level(L).

## Optimization For Next

## Autopilot

    -autopilot :- not autopilot.
    autopilot :- foundGoal, not shouldGrab, not shouldClimb, mode(explore).
    autopilot :- foundGoal, not shouldGrab, not shouldClimb, mode(escape).

## Mode Selector

    mode(explore) :- canExplore, -grabbed.
    mode(escape) :- not mode(explore), not mode(kill).
    mode(kill) :- not mode(explore), shouldKill, not shouldGrab, -grabbed.
    mode(kill) :- not mode(explore), shouldTryKill, not shouldGrab, -grabbed.

## Consistency

    wouldBump :- now(_,1,down ).
    wouldBump :- now(1,_,left ).
    wouldBump :- now(_,S,up   ), size(S).
    wouldBump :- now(S,_,right), size(S).
    inSomeMode :- isMode(M), mode(M).
    doingSomething :- isAction(A), do(A).
    foundGoal :- goal(_,_,_).
    breezeHasPossiblePit(XB,YB) :- breeze(XB,YB), possiblePit(XB,YB,XP,YP).

0 We should not go forward, since that would be our second time to bump.
    bad(0) :- do(goforward), wouldBump.

2 Don't shoot if the wumpus is already dead!
    bad(2) :- do(shoot), wumpusDead.

3 The agent is not ubiquitous.
    bad(3) :- now(X,Y,_), now(X,Z,_), Y != Z.
    bad(3) :- now(X,Y,_), now(Z,Y,_), X != Z.

4 We cannot be in more than one mode.
    bad(4) :- mode(X), mode(Y), X != Y.

5 We must be in one mode.
    bad(5) :- not inSomeMode.

6 We cannot do two things.
    bad(6) :- do(A1), do(A2), A1 != A2.

7 We must do something.
    bad(7) :- not doingSomething.

8 Wumpus detection must be accurate. There is only one wumpus.
    bad(8) :- wumpus(X1,Y), wumpus(X2,Y), X1 != X2.
    bad(8) :- wumpus(X,Y1), wumpus(X,Y2), Y1 != Y2.
    bad(8) :- wumpus(X1,Y1), wumpus(X2,Y2), X1 != X2, Y1 != Y2.

10 There is a cell outside of the world. Whut?
    bad(10) :- cell(X,_), X > S, size(S).
    bad(10) :- cell(_,Y), Y > S, size(S).

11 A breeze must have at least one possiblePit.
    bad(11) :- breeze(XB,YB), not breezeHasPossiblePit(XB,YB).

12 explored/2 and notExplored/2 must be disjoint!
    bad(12) :- explored(X,Y), notExplored(X,Y).

13 A cell cannot be -safe and explored.
    bad(13) :- cell(X,Y), -safe(X,Y), explored(X,Y).

14 We are in explore mode, have no triggers to climb or shoot, but still did not find a goal.
    bad(14) :- not foundGoal, not shouldGrab, not shouldClimb, mode(explore).

15 We are shooting even though we do not have the arrow anymore.
    bad(15) :- do(shoot), -haveArrow.

16 Cost function must be decisive.
    bad(16) :- cost(X,Y,O,X2,Y2,C1), cost(X,Y,O,X2,Y2,C2), C1 != C2.

17 Rotation cost must be decisive.
    bad(17) :- rotCost(X1,Y1,O1,X2,Y2,C1), rotCost(X1,Y1,O1,X2,Y2,C2), C1 != C2.
