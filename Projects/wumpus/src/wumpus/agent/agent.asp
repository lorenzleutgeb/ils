#maxint = 1000.

% Knowledge:
%  now(X,Y,O)   ... The agent is at position X, Y and oriented in direction O,
%  stench(X,Y)  ... The agent has perceived a stench at position X, Y.
%  breeze(X,Y)  ...               breeze
%  glitter(X,Y) ...               glitter
%  wumpusDead   ... The wumpus is dead.

% INPUT CONSISTENCY

% NOTE: size (the size of the world) is given as constant and
%       not encoded explicitly here. It will usually be set:
%        - by the calling Python agent
%        - through another ASP file.

exploredSize(X) :- explored(X,_).
exploredSize(Y) :- explored(_,Y).

sizeKnown :- bumpedSize(_).
size(S) :- not sizeKnown, Sm = #max{Se: exploredSize(Se)}, S = Sm + 1.
size(S) :- bumpedSize(S).

% Span the space of cells.
cell(X,Y) :- #int(X), #int(Y), Y > 0, X > 0, Y <= S, X <= S, size(S).

% When to shoot at the wumpus?
% TODO: Shooting the wumpus is costly. We should only
%       do so in case the wumpus blocks the way or
%       the wumpus is in the same place as the gold.
do(shoot) :- wumpus(X,Y), facing(X,Y).

% If current cell and orientation are not dangerous, explore forward.
do(goforward) :- now(X,Y,O), -danger(X,Y,O).

% If we are facing a danger, first we try to turn right.
do(turnright) :- now(X,Y,O), danger(X,Y,O), agentRight(P), -danger(X,Y,P).
% If danger is also in there, we turn left.
do(turnleft) :- now(X,Y,O), danger(X,Y,O), agentRight(P), danger(X,Y,P).

% Climb if gold is picked and back to initial cell.
shouldClimb :- canClimb, currentMode(escape).
do(climb) :- shouldClimb.

-canClimb :- not canClimb.
canClimb :- now(1,1,_).

% Signaling bumps.
bump :- now(_,1, down).
bump :- now(1,_, left).
bump :- now(_,S,   up), size(S).
bump :- now(S,_,right), size(S).

% Rotation of orientations through actions.
%  rotate(X,A,Y) ... From orientation X, action A will lead to orientation Y.
rotate(right,turnleft,up   ).
rotate(up,   turnleft,left ).
rotate(left, turnleft,down ).
rotate(down, turnleft,right).

rotate(X,turnright,Y) :- rotate(Y,turnleft,X).

% Directions from the agent's perspective.
% Only left and right, meaningful for turning 90°.
agentLeft(Y) :- now(_,_,X), rotate(X,turnleft,Y).
agentRight(Y) :- now(_,_,X), rotate(X,turnright,Y).

% Oh, look! Something is glittering...
%gold(X,Y) :- glitter(X,Y), -goldPicked.

% Pick gold if there's some in the cell.
-shouldGrab :- not shouldGrab.
shouldGrab :- now(X,Y,_), glitter(X,Y).
do(grab) :- shouldGrab.

% Cells that are in front of the agent.
facing(X,Y) :- now(X,Z,up), cell(X,Y), Z < Y.
facing(X,Y) :- now(X,Z,left), cell(X,Y), Y < Z.
facing(X,Y) :- now(Z,Y,right), cell(X,Y), Z < X.
facing(X,Y) :- now(Z,Y,down), cell(X,Y), X < Z.

% Neighboring cells along the horizontal and vertical axis.
neighbor(X1,Y1,X2,Y2,right) :- cell(X1,Y1), cell(X2,Y2), X2 = X1 + 1, Y2 = Y1.
neighbor(X1,Y1,X2,Y2,up) :- cell(X1,Y1), cell(X2,Y2), X2 = X1, Y2 = Y1 + 1.
neighbor(X1,Y1,X2,Y2,left) :- cell(X1,Y1), cell(X2,Y2), X2 = X1 - 1, Y2 = Y1.
neighbor(X1,Y1,X2,Y2,down) :- cell(X1,Y1), cell(X2,Y2), X2 = X1, Y2 = Y1 - 1.

anyNeighbor(X1,Y1,X2,Y2) :- neighbor(X1,Y1,X2,Y2,O), orientation(O).

danger(X,Y,O) :- cell(X,Y), cell(X1,Y1), neighbor(X,Y,X1,Y1,O), stench(X1,Y1), -wumpus(X1,Y1).
danger(X,Y,O) :- cell(X,Y), cell(X1,Y1), neighbor(X,Y,X1,Y1,O), breeze(X1,Y1), -pit(X1,Y1).

% To detect the wumpus, we just need to find 2 stenches out of 4.
% ISSUE: acutally this is true only if the stenches are antipodal.
wumpus(X,Y) :- X1 = X - 1, stench(X1,Y), Y1 = Y + 1, stench(X,Y1), safe(X1,Y1), -wumpusDead.
wumpus(X,Y) :- X1 = X - 1, stench(X1,Y), Y1 = Y - 1, stench(X,Y1), -wumpusDead.
wumpus(X,Y) :- cell(X,Y), X1 = X - 1, stench(X1,Y), X2 = X - 3, stench(X2,Y), -wumpusDead.
wumpus(X,Y) :- X1 = X + 1, stench(X1,Y), Y1 = Y + 1, stench(X,Y1), safe(X1,Y1), -wumpusDead.
wumpus(X,Y) :- X1 = X + 1, stench(X1,Y), Y1 = Y - 1, stench(X,Y1), -wumpusDead.
wumpus(X,Y) :- cell(X,Y), X1 = X + 1, stench(X1,Y), X2 = X + 3, stench(X2,Y), -wumpusDead.
wumpus(X,Y) :- Y1 = Y - 1, stench(X,Y1), X1 = X + 1, stench(X1,Y), safe(X1,Y1), -wumpusDead.
wumpus(X,Y) :- Y1 = Y - 1, stench(X,Y1), X1 = X - 1, stench(X1,Y), -wumpusDead.
wumpus(X,Y) :- cell(X,Y), Y1 = Y - 1, stench(X,Y1), Y2 = Y - 3, stench(X,Y2), -wumpusDead.
wumpus(X,Y) :- Y1 = Y + 1, stench(X,Y1), X1 = X + 1, stench(X1,Y), safe(X1,Y1), -wumpusDead.
wumpus(X,Y) :- Y1 = Y + 1, stench(X,Y1), X1 = X - 1, stench(X1,Y), safe(X1,Y1), -wumpusDead.
wumpus(X,Y) :- cell(X,Y), Y1 = Y + 1, stench(X,Y1), Y2 = Y + 3, stench(X,Y2), -wumpusDead.

-wumpusDetected :- not wumpusDetected.
wumpusDetected :- wumpus(_,_).

% To detect a pit, we just need to find 2 breezes out of 4.
% TODO: this causes issues.
% TODO: also, not even detecting a cross implies presence of a pit. See @ll example.
%pit(X,Y) :- X1 = X - 1, breeze(X1,Y), Y1 = Y + 1, breeze(X,Y1).
%pit(X,Y) :- X1 = X - 1, breeze(X1,Y), Y1 = Y - 1, breeze(X,Y1).
%pit(X,Y) :- cell(X,Y), X1 = X - 1, breeze(X1,Y), X2 = X - 3, breeze(X2,Y).
%pit(X,Y) :- X1 = X + 1, breeze(X1,Y), Y1 = Y + 1, breeze(X,Y1).
%pit(X,Y) :- X1 = X + 1, breeze(X1,Y), Y1 = Y - 1, breeze(X,Y1).
%pit(X,Y) :- cell(X,Y), X1 = X + 1, breeze(X1,Y), X2 = X + 3, breeze(X2,Y).
%pit(X,Y) :- Y1 = Y - 1, breeze(X,Y1), X1 = X + 1, breeze(X1,Y).
%pit(X,Y) :- Y1 = Y - 1, breeze(X,Y1), X1 = X - 1, breeze(X1,Y).
%pit(X,Y) :- cell(X,Y), Y1 = Y - 1, breeze(X,Y1), Y2 = Y - 3, breeze(X,Y2).
%pit(X,Y) :- Y1 = Y + 1, breeze(X,Y1), X1 = X + 1, breeze(X1,Y).
%pit(X,Y) :- Y1 = Y + 1, breeze(X,Y1), X1 = X - 1, breeze(X1,Y).
%pit(X,Y) :- cell(X,Y), Y1 = Y + 1, breeze(X,Y1), Y2 = Y + 3, breeze(X,Y2).

% Strategy
do(climb) :- now(1,1,_), breeze(1,2), breeze(2,1).

state(X,Y,up) :- cell(X,Y).
state(X,Y,down) :- cell(X,Y).
state(X,Y,left) :- cell(X,Y).
state(X,Y,right) :- cell(X,Y).

% Any cell where the wumpus is is not safe.
-safe(X1,Y1) :- wumpus(X1,Y1).
-safe(X2,Y2) :- anyNeighbor(X1,Y1,X2,Y2), stench(X1,Y1), -wumpusDetected.
% Any cell with an adjacent cell that has a breeze
%-safe(X1,Y1) :- anyNeighbor(X1,Y1,X1,X2), breeze(X2,Y2), -explored(X1,Y1).
-safe(X2,Y2) :- anyNeighbor(X1,Y1,X2,Y2), breeze(X1,Y1).

safe(X,Y) :- cell(X,Y), not -safe(X,Y).

currentMode(explore) :- toExplore(_,_), -grabbed.
currentMode(escape) :- not canExplore.
currentMode(escape) :- grabbed.
%currentMode(kill) :- wumpusDetected, -grabbed.

toExplore(X,Y) :- safe(X,Y), -explored(X,Y).
canExplore :- safe(X,Y), -explored(X,Y).

% Interesting candidates are those cells that we have not yet explored
% and we know that they are safe.
candidate(X,Y,O,C) :- currentMode(explore), pathCost(X,Y,O,C), orientation(O), toExplore(X,Y), -shouldGrab.
candidate(1,1,O,C) :- currentMode(escape), pathCost(1,1,O,C), orientation(O), -canClimb.

:~ goal(_,_,_,C1), goal(_,_,_,C2), C2 > C1.

foundGoal :- goal(_,_,_,_).

% Usually it is problematic if we do not find a goal. Exceptions are:
%  - We should grab the gold.
%  - We should exit the cave.
:- not foundGoal, -shouldGrab, -shouldClimb.

goal(X,Y,O,C) v -goal(X,Y,O,C) :- candidate(X,Y,O,C).

do(A) :- goal(X,Y,O,_), towards(X,Y,O,A).

% CONSISTENCY

%0 Preventing bumps.
bad(0) :- do(goforward), bump.

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
