#maxint = 1000.

% Knowledge:
%  now(X,Y,O)   ... The agent is at position X, Y and oriented in direction O,
%  stench(X,Y)  ... The agent has perceived a stench at position X, Y.
%  breeze(X,Y)  ...               breeze
%  glitter(X,Y) ...               glitter
%  wumpusDead   ... The wumpus is dead.

%diff(X1,Y1,X2,Y2) :- X1 != X2, cell(X1,Y1), cell(X2,Y2).
%diff(X1,Y1,X2,Y2) :- Y1 != Y2, cell(X1,Y1), cell(X2,Y2).

% WORLD SIZE DETECTION

exploredSize(X) :- explored(X,_).
exploredSize(Y) :- explored(_,Y).

sizeKnown :- bump(_,_).
size(S) :- not sizeKnown, Sm = #max{Se: exploredSize(Se)}, S = Sm + 1.
size(S) :- bump(S,Y), S > Y.
size(S) :- bump(X,S), S > X.

% CELLS, NEIGHBORS, FACING AND BUMPS

% Span the space of cells.
cell(X,Y) :- #int(X), #int(Y), Y > 0, X > 0, Y <= S, X <= S, size(S).

% Neighboring cells along the horizontal and vertical axis.
neighbor(X1,Y1,X2,Y2,right) :- cell(X1,Y1), cell(X2,Y2), X2 = X1 + 1, Y2 = Y1.
neighbor(X1,Y1,X2,Y2,up   ) :- cell(X1,Y1), cell(X2,Y2), X2 = X1, Y2 = Y1 + 1.
neighbor(X1,Y1,X2,Y2,left ) :- cell(X1,Y1), cell(X2,Y2), X2 = X1 - 1, Y2 = Y1.
neighbor(X1,Y1,X2,Y2,down ) :- cell(X1,Y1), cell(X2,Y2), X2 = X1, Y2 = Y1 - 1.

anyNeighbor(X1,Y1,X2,Y2) :- neighbor(X1,Y1,X2,Y2,O), orientation(O).

% Cells that are in front of the agent.
facing(X,Y) :- cell(X,Y), Z < Y, now(X,Z,up   ).
facing(X,Y) :- cell(X,Y), Y < Z, now(X,Z,left ).
facing(X,Y) :- cell(X,Y), Z < X, now(Z,Y,right).
facing(X,Y) :- cell(X,Y), X < Z, now(Z,Y,down ).

% Signaling bumps.
wouldBump :- now(_,1,down ).
wouldBump :- now(1,_,left ).
wouldBump :- now(_,S,up   ), size(S).
wouldBump :- now(S,_,right), size(S).

% TODO: Why does this break everything?
-explored(X,Y) :- cell(X,Y), not explored(X,Y).
-notExplored(X,Y) :- cell(X,Y), not notExplored(X,Y).
notExplored(X,Y) :- cell(X,Y), not explored(X,Y).

% HIGH PRIORITY ACTIONS

% When to shoot at the wumpus?
% TODO: Shooting the wumpus is costly. We should only
%       do so in case the wumpus blocks the way or
%       the wumpus is in the same place as the gold.
%do(shoot) :- wumpus(X,Y), facing(X,Y), currentMode(kill).

% Pick gold if there's some in the cell.
-shouldGrab :- not shouldGrab.
shouldGrab :- now(X,Y,_), glitter(X,Y).
do(grab) :- shouldGrab.

% Climb if gold is picked and back to initial cell.
shouldClimb :- canClimb, currentMode(escape).
-shouldClimb :- not shouldClimb.
do(climb) :- shouldClimb.

-canClimb :- not canClimb.
canClimb :- now(1,1,_).

% DETECTION OF PITS AND WUMPUS

% To detect the wumpus, we just need to find 2 stenches out of 4.
% ISSUE: acutally this is true only if the stenches are antipodal.
wumpus(X,Y) :- X1 = X - 1, stench(X1,Y), Y1 = Y + 1, stench(X,Y1), explored(X1,Y1), -wumpusDead.
wumpus(X,Y) :- X1 = X - 1, stench(X1,Y), Y1 = Y - 1, stench(X,Y1), explored(X1,Y1), -wumpusDead.
%wumpus(X,Y) :- cell(X,Y), X1 = X - 1, stench(X1,Y), X2 = X - 3, stench(X2,Y), -wumpusDead.
wumpus(X,Y) :- X1 = X + 1, stench(X1,Y), Y1 = Y + 1, stench(X,Y1), explored(X1,Y1), -wumpusDead.
wumpus(X,Y) :- X1 = X + 1, stench(X1,Y), Y1 = Y - 1, stench(X,Y1), explored(X1,Y1), -wumpusDead.
wumpus(X,Y) :- cell(X,Y), X1 = X + 1, stench(X1,Y), X2 = X - 1, stench(X2,Y), -wumpusDead.
wumpus(X,Y) :- Y1 = Y - 1, stench(X,Y1), X1 = X + 1, stench(X1,Y), explored(X1,Y1), -wumpusDead.
wumpus(X,Y) :- Y1 = Y - 1, stench(X,Y1), X1 = X - 1, stench(X1,Y), explored(X1,Y1), -wumpusDead.
wumpus(X,Y) :- cell(X,Y), Y1 = Y - 1, stench(X,Y1), Y2 = Y + 1, stench(X,Y2), -wumpusDead.
wumpus(X,Y) :- Y1 = Y + 1, stench(X,Y1), X1 = X + 1, stench(X1,Y), explored(X1,Y1), -wumpusDead.
wumpus(X,Y) :- Y1 = Y + 1, stench(X,Y1), X1 = X - 1, stench(X1,Y), explored(X1,Y1), -wumpusDead.
%wumpus(X,Y) :- cell(X,Y), Y1 = Y + 1, stench(X,Y1), Y2 = Y + 3, stench(X,Y2), -wumpusDead.

% TODO: Possibly shorter wumpus detection?
%wumpus(X1,Y1) :- anyNeighbor(X1,Y1,X2,Y2), anyNeighbor(X1,Y1,X3,Y3), diff(X2,Y2,X3,Y3), stench(X2,Y2), stench()

-wumpusDetected :- not wumpusDetected.
wumpusDetected :- wumpus(_,_).

% Any explored cell certainly cannot be a pit, otherwise we would be dead by now.
cannotBePit(X,Y) :- explored(X,Y).
% If we have explored a cell already and felt no brezee, then no neighbor be a pit.
cannotBePit(X2,Y2) :- -breeze(X1,Y1), anyNeighbor(X1,Y1,X2,Y2).
possiblePit(XB,YB,XP,YP) :- breeze(XB,YB), anyNeighbor(XB,YB,XP,YP), not cannotBePit(XP,YP).
%pit(XP,YP) :- possiblePit(XB,YB,XP,YP), 1 = #count{XPc,YPc: possiblePit(XB,YB,XPc,YPc)}.

% SAFETY OF CELLS

% Any cell where the wumpus is is not safe.
-safe(X1,Y1) :- wumpus(X1,Y1).
-safe(X2,Y2) :- anyNeighbor(X1,Y1,X2,Y2), stench(X1,Y1), -wumpusDetected, notExplored(X2,Y2).
-safe(X2,Y2) :- possiblePit(X1,Y1,X2,Y2).

safe(X,Y) :- cell(X,Y), not -safe(X,Y).

toExplore(X,Y) :- safe(X,Y), notExplored(X,Y).
canExplore :- toExplore(_,_).

% Interesting candidates are those cells that we have not yet explored
% and we know that they are safe.
candidate(X,Y,O,C) :- currentMode(explore), pathCost(X,Y,O,C), orientation(O), toExplore(X,Y), -shouldGrab.
candidate(1,1,O,C) :- currentMode(escape), pathCost(1,1,O,C), orientation(O), -shouldClimb.

:~ candidate(_,_,_,C1), candidate(X,Y,O,C2), C2 > C1, goal(X,Y,O,C2). [5:1]
:~ goal(_,_,_,C1), goal(_,_,_,C2), C2 > C1. [4:1]
:~ goal(X1,_,_,C), goal(X2,_,_,C), X1 < X2. [3:1]
:~ goal(X,Y1,_,C), goal(X,Y2,_,C), Y1 < Y2. [2:1]
:~ goal(X,Y,O1,C), goal(X,Y,O2,C), O1 < O2. [1:1]

foundGoal :- goal(_,_,_,_).

% Usually it is problematic if we do not find a goal. Exceptions are:
%  - We should grab the gold.
%  - We should exit the cave.
:- not foundGoal, -shouldGrab, -shouldClimb.

goal(X,Y,O,C) v -goal(X,Y,O,C) :- candidate(X,Y,O,C).

currentMode(explore) :- toExplore(_,_), -grabbed.
currentMode(escape) :- not canExplore.
currentMode(escape) :- grabbed.
%currentMode(kill) :- wumpusDetected, -grabbed.

do(A) :- goal(X,Y,O,_), towards(X,Y,O,A), -shouldGrab, -shouldClimb.

% CONSISTENCY

%0 Preventing bumps.
bad(0) :- do(goforward), wouldBump.

%1 Cannot pick up something that's already been picked!
% TODO: how to remove gold from knowledge once it's been collected?
%       SOLUTION: at next call, add -gold(X,Y) to KB.
bad(1) :- gold(X,Y), now(X,Y,_), goldPicked.

%2 Don't shoot if the wumpus is already dead!
bad(2) :- do(shoot), wumpusDead.

%3 The agent is not ubiquitous.
bad(3) :- now(X,Y,_), now(X,Z,_), Y != Z.
bad(3) :- now(X,Y,_), now(Z,Y,_), X != Z.

%4 We cannot be in more than one mode.
bad(4) :- currentMode(X), currentMode(Y), X != Y.

%5 We must be in one mode.
inSomeMode :- mode(M), currentMode(M).
bad(5) :- not inSomeMode.

%6 We cannot do two things.
bad(6) :- do(A1), do(A2), A1 != A2.

%7 We must do something.
doingSomething :- action(A), do(A).
bad(7) :- not doingSomething.

%8 Wumpus detection must be accurate. There is only one wumpus.
bad(8) :- wumpus(X1,Y), wumpus(X2,Y), X1 != X2.
bad(8) :- wumpus(X,Y1), wumpus(X,Y2), Y1 != Y2.
bad(8) :- wumpus(X1,Y1), wumpus(X2,Y2), X1 != X2, Y1 != Y2.

%9 A pit must be a possible pit.
%pitHasBreeze(X,Y) :- pit(X,Y), breeze(XB,YB), possiblePit(XB,YB,X,Y).
%bad(9) :- pit(X,Y), not pitHasBreeze(X,Y).

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
