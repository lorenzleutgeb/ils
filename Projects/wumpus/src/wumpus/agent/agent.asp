#maxint = 1000.

% Knowledge:
%  now(X,Y,O)   ... The agent is at position X, Y and oriented in direction O,
%  stench(X,Y)  ... The agent has perceived a stench at position X, Y.
%  breeze(X,Y)  ...               breeze
%  glitter(X,Y) ...               glitter
%  wumpusDead   ... The wumpus is dead.
%  haveArrow    ... We have an arrow that we may shoot.

% We designate two orthogonal orientations as axes.
axis(0..1).

% WORLD SIZE DETECTION

exploredSize(X) :- explored(X,_).
exploredSize(Y) :- explored(_,Y).

sizeKnown :- bump(_,_).
size(S) :- not sizeKnown, Sm = #max{Se: exploredSize(Se)}, S = Sm + 1.
size(S) :- bump(Sm,Y), Sm > Y, S = Sm - 1.
size(S) :- bump(X,Sm), Sm > X, S = Sm - 1.

% CELLS, NEIGHBORS, FACING AND BUMPS

% Span the space of cells.
cell(X,Y) :- #int(X), #int(Y), Y > 0, X > 0, Y <= S, X <= S, size(S).

diff(X1,Y1,X2,Y2) :- X1 != X2, cell(X1,Y1), cell(X2,Y2).
diff(X1,Y1,X2,Y2) :- Y1 != Y2, cell(X1,Y1), cell(X2,Y2).

% Neighboring cells along the horizontal and vertical axis.
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

% Cells that agree on one component.
facing(X,Z,up,X,Y) :- cell(X,Y), Z < Y, cell(X,Z).
facing(X,Z,down,X,Y) :- cell(X,Y), Y < Z, cell(X,Z).
facing(Z,Y,right,X,Y) :- cell(X,Y), Z < X, cell(Z,Y).
facing(Z,Y,left,X,Y) :- cell(X,Y), X < Z, cell(Z,Y).

-facing(X1,Y1,O,X2,Y2) :- not facing(X1,Y1,O,X2,Y2), cell(X1,Y1), isOrientation(O), cell(X2,Y2).

% Complete information about information. We only do this here and
% not in Python since we might have assumed a size.
-explored(X,Y) :- cell(X,Y), not explored(X,Y).

% DO

shouldShoot :- mode(kill), now(X,Y,O), canKill(X,Y,O).
shouldShoot :- mode(kill), now(X,Y,O), canTryKill(X,Y,O).
do(shoot) :- shouldShoot.

% Pick gold if there's some in the cell, independently of the current mode.
shouldGrab :- now(X,Y,_), glitter(X,Y).
do(grab) :- shouldGrab.

% Climb if gold is picked and back to initial cell.
shouldClimb :- now(1,1,_), mode(escape).
do(climb) :- shouldClimb.

% Generally we will be turning and go forward towards a goal. Exceptions are when we
% want to take high priority actions like grabbing, climbing or shooting.
do(A) :- goal(X,Y,O,_), towards(X,Y,O,A), not shouldGrab, not shouldClimb, not shouldShoot.

% DETECTION OF WUMPUS

wumpus(X1,Y1) :- square(X1,Y1,X2,Y2,X3,Y3,X4,Y4), stench(X2,Y2), stench(X3,Y3), explored(X4,Y4), -wumpusDead.

% Antipodal matching.
wumpus(X2,Y2) :- triple(X1,Y1,X2,Y2,X3,Y3), stench(X1,Y1), stench(X3,Y3), -wumpusDead.

% Corner case.
wumpus(XW,YW) :- stench(XC,YC), corner(XC,YC), twoNeighbors(XC,YC,XW,YW,XE,YE), explored(XE,YE), -wumpusDead.

% Auxiliary flag to signal detection of wumpus.
wumpusDetected :- cell(X,Y), wumpus(X,Y).

% If wumpus is not certainly detected, we must exclude other cells where it might be.
possibleWumpus(X2,Y2) :- anyNeighbor(X1,Y1,X2,Y2), stench(X1,Y1), not wumpusDetected, -explored(X2,Y2), -wumpusDead, not shotAt(X2,Y2).
shotAt(X,Y) :- shot(XS,YS,OS), facing(XS,YS,OS,X,Y).

% DETECTION OF PITS

% Any explored cell certainly cannot be a pit, otherwise we would be dead by now.
-pit(X,Y) :- explored(X,Y).

% If we have explored a cell already and felt no brezee, then no neighbor can be a pit.
-pit(X2,Y2) :- -breeze(X1,Y1), anyNeighbor(X1,Y1,X2,Y2).

% A neighbor of a breeze is a possible pit if it can be.
possiblePit(XB,YB,XP,YP) :- breeze(XB,YB), anyNeighbor(XB,YB,XP,YP), not -pit(XP,YP).

% SAFETY OF CELLS

% Any cell where the wumpus is is not safe.
safe(X,Y) :- explored(X,Y).
-safe(X1,Y1) :- wumpus(X1,Y1).
-safe(X1,Y1) :- possibleWumpus(X1,Y1).
-safe(X2,Y2) :- possiblePit(X1,Y1,X2,Y2).

safe(X,Y) :- cell(X,Y), not -safe(X,Y).

% EXPLORE MODE

reachable(X,Y) :- pathCost(X,Y,_,_).

toExplore(X,Y) :- reachable(X,Y), safe(X,Y), -explored(X,Y).

% Auxiliary flag to signal whether we can still explore further.
canExplore :- toExplore(_,_).

% Interesting candidates are those cells that we have not yet explored
% and we know that they are safe.
candidate(X,Y,O,C) :- pathCost(X,Y,O,C), isOrientation(O), mode(explore), toExplore(X,Y).

% ESCAPE MODE

candidate(1,1,O,C) :- pathCost(1,1,O,C), isOrientation(O), mode(escape).

% KILL MODE

canKill(XS,YS,OS) :- wumpus(XW,YW), -wumpusDead, safe(XS,YS), facing(XS,YS,OS,XW,YW), haveArrow.
shouldKill :- canKill(_,_,_), wumpus(XW,YW), not possiblePit(XB,YB,XW,YW), cell(XB,YB).

canTryKill(X,Y,O) :- possibleWumpus(XC,YC), safe(X,Y), facing(X,Y,O,XC,YC), not possiblePit(XB,YB,X,Y), cell(XB,YB), haveArrow.
shouldTryKill :- not shouldKill, canTryKill(_,_,_).

candidate(XS,YS,OS,C) :- pathCost(XS,YS,OS,C), canKill(XS,YS,OS), mode(kill).
candidate(XS,YS,OS,C) :- pathCost(XS,YS,OS,C), canTryKill(XS,YS,OS), mode(kill).

% OPTIMIZATION FOR GOAL

% Minimize cost of goals:
:~ candidate(_,_,_,C1), candidate(X,Y,O,C2), C2 > C1, goal(X,Y,O,C2).

% Tie breaking:
:- goal(_,_,_,C1), goal(_,_,_,C2), C2 > C1.
:- goal(X1,_,_,C), goal(X2,_,_,C), X1 < X2.
:- goal(X,Y1,_,C), goal(X,Y2,_,C), Y1 < Y2.
:- goal(X,Y,O1,C), goal(X,Y,O2,C), O1 < O2.

goal(X,Y,O,C) v -goal(X,Y,O,C) :- candidate(X,Y,O,C).

% AUTOPILOT

%autopilot :- foundGoal, not shouldGrab, not shouldClimb, mode(explore).

% MODE SELECTOR

mode(explore) :- canExplore, -grabbed.
mode(escape) :- not mode(explore), not mode(kill).
mode(kill) :- not mode(explore), shouldKill, -grabbed.
mode(kill) :- not mode(explore), shouldTryKill, -grabbed.

% CONSISTENCY

%0 We should not go forward, since that would be our second time to bump.
wouldBump :- now(_,1,down ).
wouldBump :- now(1,_,left ).
wouldBump :- now(_,S,up   ), size(S).
wouldBump :- now(S,_,right), size(S).
bad(0) :- do(goforward), wouldBump.

%2 Don't shoot if the wumpus is already dead!
bad(2) :- do(shoot), wumpusDead.

%3 The agent is not ubiquitous.
bad(3) :- now(X,Y,_), now(X,Z,_), Y != Z.
bad(3) :- now(X,Y,_), now(Z,Y,_), X != Z.

%4 We cannot be in more than one mode.
bad(4) :- mode(X), mode(Y), X != Y.

%5 We must be in one mode.
inSomeMode :- isMode(M), mode(M).
bad(5) :- not inSomeMode.

%6 We cannot do two things.
bad(6) :- do(A1), do(A2), A1 != A2.

%7 We must do something.
doingSomething :- isAction(A), do(A).
bad(7) :- not doingSomething.

%8 Wumpus detection must be accurate. There is only one wumpus.
bad(8) :- wumpus(X1,Y), wumpus(X2,Y), X1 != X2.
bad(8) :- wumpus(X,Y1), wumpus(X,Y2), Y1 != Y2.
bad(8) :- wumpus(X1,Y1), wumpus(X2,Y2), X1 != X2, Y1 != Y2.

%10 There is a cell outside of the world. Whut?
bad(10) :- cell(X,_), X > S, size(S).
bad(10) :- cell(_,Y), Y > S, size(S).

%11 A breeze must have at least one possiblePit.
breezeHasPossiblePit(XB,YB) :- breeze(XB,YB), possiblePit(XB,YB,XP,YP).
bad(11) :- breeze(XB,YB), not breezeHasPossiblePit(XB,YB).

%12 explored/2 and notExplored/2 must be disjoint!
bad(12) :- explored(X,Y), notExplored(X,Y).

%13 A cell cannot be -safe and explored.
bad(13) :- cell(X,Y), -safe(X,Y), explored(X,Y).

%14 We are in explore mode, have no triggers to climb or shoot, but still did not find a goal.
foundGoal :- goal(_,_,_,_).
bad(14) :- not foundGoal, not shouldGrab, not shouldClimb, mode(explore).

%15 We are shooting even though we do not have the arrow anymore.
bad(15) :- do(shoot), -haveArrow.
