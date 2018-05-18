#maxint = 1000.

% Knowledge:
%  now(X,Y,O)   ... The agent is at position X, Y and oriented in direction O,
%  stench(X,Y)  ... The agent has perceived a stench at position X, Y.
%  breeze(X,Y)  ...               breeze
%  glitter(X,Y) ...               glitter
%  wumpus_dead  ... The wumpus is dead.

% INPUT CONSISTENCY

% The agent is not ubiquitous.
:- now(X,Y,_), now(X,Z,_), Y != Z.
:- now(X,Y,_), now(Z,Y,_), X != Z.

% NOTE: size (the size of the world) is given as constant and
%       not encoded explicitly here. It will usually be set:
%        - by the calling Python agent
%        - through another ASP file.
%       In case we bump, the Python agent will recognize this
%       and decrease size accordingly.

% Span the space of cells.
cell(X,Y) :- #int(X), #int(Y), Y > 0, X > 0, Y <= worldSize, X <= worldSize.

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
do(climb) :- gold_picked, now(1,1,_).

% Signaling bumps.
bump :- now(   _,worldSize,   up).
bump :- now(   _,   1, down).
bump :- now(   1,   _, left).
bump :- now(worldSize,   _,right).

% Preventing bumps.
:- do(goforward), bump.

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
gold(X,Y) :- glitter(X,Y), -gold_picked.

% Pick gold if there's some in the cell.
do(grab) :- now(X,Y,_), gold(X,Y).

% Cells that are in front of the agent.
facing(X,Y) :- now(X,Z,right), cell(X,Y), Z < Y.
facing(X,Y) :- now(X,Z,left), cell(X,Y), Y < Z.
facing(X,Y) :- now(Z,Y,up), cell(X,Y), Z < X.
facing(X,Y) :- now(Z,Y,down), cell(X,Y), X < Z.

% Result should be do(A).

% Cannot pick up something that's already been picked!
% TODO: how to remove gold from knowledge once it's been collected?
%       SOLUTION: at next call, add -gold(X,Y) to KB.
:- gold(X,Y), now(X,Y,_), gold_picked.

% Don't shoot if the wumpus is already dead!
:- do(shoot), wumpusDead.

% Neighboring cells along the horizontal and vertical axis.
neighbor(X1,Y1,X2,Y2,right) :- cell(X1,Y1), cell(X2,Y2), X2 = X1 + 1, Y2 = Y1.
neighbor(X1,Y1,X2,Y2,up) :- cell(X1,Y1), cell(X2,Y2), X2 = X1, Y2 = Y1 + 1.
neighbor(X1,Y1,X2,Y2,left) :- cell(X1,Y1), cell(X2,Y2), X2 = X1 - 1, Y2 = Y1.
neighbor(X1,Y1,X2,Y2,down) :- cell(X1,Y1), cell(X2,Y2), X2 = X1, Y2 = Y1 - 1.

anyNeighbor(X1,Y1,X2,Y2) :- neighbor(X1,Y1,X2,Y2,O), orientation(O).

danger(X,Y,O) :- cell(X,Y), cell(X1,Y1), neighbor(X,Y,X1,Y1,O), stench(X1,Y1), -wumpus(X1,Y1).
danger(X,Y,O) :- cell(X,Y), cell(X1,Y1), neighbor(X,Y,X1,Y1,O), breeze(X1,Y1), -pit(X1,Y1).

% To detect the wumpus, we just need to find 2 stenches out of 4.
wumpus(X,Y) :- X1 = X - 1, stench(X1,Y), Y1 = Y + 1, stench(X,Y1).
wumpus(X,Y) :- X1 = X - 1, stench(X1,Y), Y1 = Y - 1, stench(X,Y1).
wumpus(X,Y) :- cell(X,Y), X1 = X - 1, stench(X1,Y), X2 = X - 3, stench(X2,Y).
wumpus(X,Y) :- X1 = X + 1, stench(X1,Y), Y1 = Y + 1, stench(X,Y1).
wumpus(X,Y) :- X1 = X + 1, stench(X1,Y), Y1 = Y - 1, stench(X,Y1).
wumpus(X,Y) :- cell(X,Y), X1 = X + 1, stench(X1,Y), X2 = X + 3, stench(X2,Y).
wumpus(X,Y) :- Y1 = Y - 1, stench(X,Y1), X1 = X + 1, stench(X1,Y).
wumpus(X,Y) :- Y1 = Y - 1, stench(X,Y1), X1 = X - 1, stench(X1,Y).
wumpus(X,Y) :- cell(X,Y), Y1 = Y - 1, stench(X,Y1), Y2 = Y - 3, stench(X,Y2).
wumpus(X,Y) :- Y1 = Y + 1, stench(X,Y1), X1 = X + 1, stench(X1,Y).
wumpus(X,Y) :- Y1 = Y + 1, stench(X,Y1), X1 = X - 1, stench(X1,Y).
wumpus(X,Y) :- cell(X,Y), Y1 = Y + 1, stench(X,Y1), Y2 = Y + 3, stench(X,Y2).

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

% Penalty for doing nothing?
%cost(X,Y,O,X,Y,O,n) :- state(X,Y,O).
% Cost for rotating is 1.
%cost(X,Y,O1,X,Y,O2,1) :- cell(X,Y), rotate(O1,_,O2).
% Cost for going in the same direction is 1.
%cost(X1,Y1,O,X2,Y2,O,1) :- neighbor(X1,Y1,X2,Y2,O).

% TODO: This transitive monster just blows up like crazy...
%cost(X1,Y1,O1,X3,Y3,O3,C3) :-
%	state(X1,Y1,O1),
%	state(X2,Y2,O2),
%	state(X3,Y3,O3),
%	cost(X1,Y1,O1,X2,Y2,O2,C1),
%	cost(X2,Y2,O2,X3,Y3,O3,C2),
%	C3 = C1 + C2.

%pathCost(X2,Y2,O2,C) :- now(X1,Y1,O1), state(X2,Y2,O2), C = #min{Cx: cost(X1,Y1,O1,X2,Y2,O2,Cx)}.

% Any cell where the wumpus is is not safe.
-safe(X1,Y1) :- wumpus(X1,Y1), -explored(X1,Y1).
% Any cell with an adjacent cell that has a breeze
-safe(X1,Y1) :- anyNeighbor(X1,Y1,X1,X2), breeze(X2,Y2), -explored(X1,Y1).
-safe(X1,Y1) :- anyNeighbor(X1,Y1,X1,X2), breeze(X1,X2).

safe(X,Y) :- cell(X,Y), not -safe(X,Y).

% Interesting candidates are those cells that we have not yet explored
% and we know that they are safe.
candidate(X,Y) :- safe(X,Y), -explored(X,Y).

% TODO: The goal should be the candidate with the least cost to reach.
goal(X1,Y1) :-
	candidate(X1,Y1),
	candidate(X2,Y2),
	X1 != X2,
	Y1 != Y2,
	pathCost(X1,Y1,_,C1),
	pathCost(X2,Y2,_,C2),
	C1 < C2.
