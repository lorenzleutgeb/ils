#maxint = 1000.

% Knowledge:
%  now(X,Y,O)   ... The agent is at position X, Y and oriented in direction O,
%  stench(X,Y)  ... The agent has perceived a stench at position X, Y.
%  breeze(X,Y)  ...               breeze
%  glitter(X,Y) ...               glitter
%  wumpusDead   ... The wumpus is dead.
%  haveArrow    ... We have an arrow that we may shoot.

diff(X1,Y1,X2,Y2) :- X1 != X2, cell(X1,Y1), cell(X2,Y2).
diff(X1,Y1,X2,Y2) :- Y1 != Y2, cell(X1,Y1), cell(X2,Y2).

axis(up).
axis(right).

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

% Neighboring cells along the horizontal and vertical axis.
neighbor(X1,Y1,X2,Y2,right) :- cell(X1,Y1), cell(X2,Y2), X2 = X1 + 1, Y2 = Y1.
neighbor(X1,Y1,X2,Y2,up   ) :- cell(X1,Y1), cell(X2,Y2), X2 = X1, Y2 = Y1 + 1.
neighbor(X1,Y1,X2,Y2,left ) :- cell(X1,Y1), cell(X2,Y2), X2 = X1 - 1, Y2 = Y1.
neighbor(X1,Y1,X2,Y2,down ) :- cell(X1,Y1), cell(X2,Y2), X2 = X1, Y2 = Y1 - 1.

anyNeighbor(X1,Y1,X2,Y2) :- neighbor(X1,Y1,X2,Y2,O), orientation(O).

% Cells that agree on one component.
facing(X,Z,up,X,Y) :- cell(X,Y), Z < Y, cell(X,Z).
facing(X,Z,down,X,Y) :- cell(X,Y), Y < Z, cell(X,Z).
facing(Z,Y,right,X,Y) :- cell(X,Y), Z < X, cell(Z,Y).
facing(Z,Y,left,X,Y) :- cell(X,Y), X < Z, cell(Z,Y).

% Complete information about information. We only do this here and
% not in Python since we might have assumed a size.
-explored(X,Y) :- cell(X,Y), not explored(X,Y).

% HIGH PRIORITY ACTIONS

% When to shoot at the wumpus?
% TODO: Shooting the wumpus is costly. We should only
%       do so in case the wumpus blocks the way or
%       the wumpus is in the same place as the gold.
%do(shoot) :- wumpus(X,Y), facing(X,Y), currentMode(kill).

shouldShoot :- currentMode(kill), canKillWumpus(X,Y,O), now(X,Y,O).
do(shoot) :- shouldShoot.

% Pick gold if there's some in the cell.
shouldGrab :- now(X,Y,_), glitter(X,Y).
do(grab) :- shouldGrab.

% Climb if gold is picked and back to initial cell.
shouldClimb :- now(1,1,_), currentMode(escape).
do(climb) :- shouldClimb.

% DETECTION OF WUMPUS

wumpus(X1,Y1) :- anyNeighbor(X1,Y1,X2,Y2), anyNeighbor(X1,Y1,X3,Y3), diff(X2,Y2,X3,Y3), anyNeighbor(X2,Y2,X4,Y4), anyNeighbor(X3,Y3,X4,Y4), diff(X1,Y1,X4,Y4), stench(X2,Y2), stench(X3,Y3), explored(X4,Y4), -wumpusDead.

% Antipodal matching.
%wumpus(X2,Y2) :- neighbor(X1,Y1,X2,Y2,A), neighbor(X2,Y2,X3,Y3,A), stench(X1,Y1), stench(X3,Y3), diff(X1,Y1,X3,Y3), axis(A), -wumpusDead.

% Auxiliary flag to signal detection of wumpus.
wumpusDetected :- cell(X,Y), wumpus(X,Y).

canKillWumpus(XS,YS,OS) :- wumpus(XW,YW), -wumpusDead, safe(XS,YS), facing(XS,YS,OS,XW,YW), haveArrow.
shouldKillWumpus :- canKillWumpus(_,_,_), wumpus(XW,YW), not possiblePit(XB,YB,XW,YW), cell(XB,YB).

candidate(XS,YS,OS,C) :- pathCost(XS,YS,OS,C), canKillWumpus(XS,YS,OS), currentMode(kill).

% If wumpus is not certainly detected, we must exclude other cells where it might be.
possibleWumpus(X2,Y2) :- anyNeighbor(X1,Y1,X2,Y2), stench(X1,Y1), not wumpusDetected, -explored(X2,Y2), -wumpusDead.

% DETECTION OF PITS

% Any explored cell certainly cannot be a pit, otherwise we would be dead by now.
cannotBePit(X,Y) :- explored(X,Y).

% If we have explored a cell already and felt no brezee, then no neighbor can be a pit.
cannotBePit(X2,Y2) :- -breeze(X1,Y1), anyNeighbor(X1,Y1,X2,Y2).

% A neighbor of a breeze is a possible pit if it can be.
possiblePit(XB,YB,XP,YP) :- breeze(XB,YB), anyNeighbor(XB,YB,XP,YP), not cannotBePit(XP,YP).

% SAFETY OF CELLS

% Any cell where the wumpus is is not safe.
safe(X,Y) :- explored(X,Y).
-safe(X1,Y1) :- wumpus(X1,Y1).
-safe(X1,Y1) :- possibleWumpus(X1,Y1).
-safe(X2,Y2) :- possiblePit(X1,Y1,X2,Y2).

safe(X,Y) :- cell(X,Y), not -safe(X,Y).

reachable(X,Y) :- pathCost(X,Y,_,_).

toExplore(X,Y) :- reachable(X,Y), safe(X,Y), -explored(X,Y).

% Auxiliary flag to signal whether we can still explore further.
canExplore :- toExplore(_,_).

% Interesting candidates are those cells that we have not yet explored
% and we know that they are safe.
candidate(X,Y,O,C) :- pathCost(X,Y,O,C), orientation(O), currentMode(explore), toExplore(X,Y).
candidate(1,1,O,C) :- pathCost(1,1,O,C), orientation(O), currentMode(escape).

%goal(X,Y,O,C) :- candidate(X,Y,O,C), 1 = #count{Xc,Yc,Oc,Cc: candidate(Xc,Yc,Oc,Cc)}.
%strange(X,Y) :- candidate(X,Y,O,C), 1 = #count{Xc,Yc,Oc,Cc: candidate(Xc,Yc,Oc,Cc)}.

% Minimize cost of goals:
:~ candidate(_,_,_,C1), candidate(X,Y,O,C2), C2 > C1, goal(X,Y,O,C2).

% Tie breaking:
:- goal(_,_,_,C1), goal(_,_,_,C2), C2 > C1.
:- goal(X1,_,_,C), goal(X2,_,_,C), X1 < X2.
:- goal(X,Y1,_,C), goal(X,Y2,_,C), Y1 < Y2.
:- goal(X,Y,O1,C), goal(X,Y,O2,C), O1 < O2.

foundGoal :- goal(_,_,_,_).

goal(X,Y,O,C) v -goal(X,Y,O,C) :- candidate(X,Y,O,C).

do(A) :- goal(X,Y,O,_), towards(X,Y,O,A), not shouldGrab, not shouldClimb, not shouldShoot.

%autopilot :- foundGoal, not shouldGrab, not shouldClimb, currentMode(explore).

% MODES

currentMode(explore) :- canExplore, -grabbed.
currentMode(escape) :- not currentMode(explore), not currentMode(kill).
currentMode(kill) :- not currentMode(explore), canKillWumpus(_,_,_), shouldKillWumpus.

% CONSISTENCY

%0 We should not go forward, since that would be our second time to bump.
wouldBump :- now(_,1,down ).
wouldBump :- now(1,_,left ).
wouldBump :- now(_,S,up   ), size(S).
wouldBump :- now(S,_,right), size(S).
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

%14 We are in explore mode, have no triggers to climb or shoot, but still did not find a goal.
bad(14) :- not foundGoal, not shouldGrab, not shouldClimb, mode(explore).
