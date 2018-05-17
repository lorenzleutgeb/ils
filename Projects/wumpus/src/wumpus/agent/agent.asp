#maxint = 100.

% NOTE: size (the size of the world) is given as constant and
%       not encoded explicitly here. It will usually be set:
%        - by the calling Python agent
%        - through another ASP file.

cell(1,1).
cell(1,2).
cell(1,3).
cell(1,4).
cell(2,1).
cell(2,2).
cell(2,3).
cell(2,4).
cell(3,1).
cell(3,2).
cell(3,3).
cell(3,4).
cell(4,1).
cell(4,2).
cell(4,3).
cell(4,4).

% When to shoot at the wumpus?
action(shoot) :- wumpus(X,Y), facing(X,Y).

% If current cell and orientation are not dangerous, explore forward.
action(goforward) :- position(X,Y), orientation(O), -danger(X,Y,O).

% If we are facing a danger, first we try to turn right.
action(turnright) :- position(X,Y), orientation(O), danger(X,Y,O), agentRight(P), -danger(X,Y,P).
% If danger is also in there, we turn left.
action(turnleft) :- position(X,Y), orientation(O), danger(X,Y,O), agentRight(P), danger(X,Y,P).

% Climb if gold is picked and back to initial cell.
action(climb) :- gold_picked, position(1,1).

% The agent is not ubiquitous.
:- position(X,Y), position(X,Z), Y != Z.
:- position(X,Y), position(Z,Y), X != Z.

% Signaling bumps.

bump(up) :- position(_,size).
bump(down) :- position(_,1).
bump(left) :- position(1,_).
bump(right) :- position(size,_).

% Directions from the agent's perspective.
% Only left and right, meaningful for turning 90°.

agentLeft(up) :- orientation(right).
agentLeft(left) :- orientation(up).
agentLeft(down) :- orientation(left).
agentLeft(right) :- orientation(down).

agentRight(up) :- orientation(left).
agentRight(left) :- orientation(down).
agentRight(down) :- orientation(right).
agentRight(right) :- orientation(up).

% Preventing bumps.
:- action(goforward), orientation(o), bump(o).

% Oh, look! Something is glittering...
gold(X,Y) :- glitter(X,Y), -gold_picked.

% Cells that are in front of the agent.
facing(X,Y) :- position(X,Z), cell(X,Y), Z < Y, orientation(right).
facing(X,Y) :- position(X,Z), cell(X,Y), Y < Z, orientation(left).
facing(X,Y) :- position(Z,Y), cell(X,Y), Z < X, orientation(up).
facing(X,Y) :- position(Z,Y), cell(X,Y), X < Z, orientation(down).

% Result should be action(A).

% Pick gold if there's some in the cell.
action(grab) :- position(X,Y), gold(X,Y).

% Cannot pick up something that's already been picked!
% TODO: how to remove gold from knowledge once it's been collected?
%       SOLUTION: at next call, add -gold(X,Y) to KB.
:- gold(X,Y), position(X,Y), gold_picked.

% Don't shoot if the wumpus is already dead!
:- action(shoot), wumpus_dead.

% Neighboring cells along the horizontal and vertical axis.
neighbor(X1,Y1,X2,Y2,right) :- cell(X1,Y1), cell(X2,Y2), X2 = X1 + 1, Y2 = Y1.
neighbor(X1,Y1,X2,Y2,up) :- cell(X1,Y1), cell(X2,Y2), X2 = X1, Y2 = Y1 + 1.
neighbor(X1,Y1,X2,Y2,left) :- cell(X1,Y1), cell(X2,Y2), X2 = X1 - 1, Y2 = Y1.
neighbor(X1,Y1,X2,Y2,down) :- cell(X1,Y1), cell(X2,Y2), X2 = X1, Y2 = Y1 - 1.

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
pit(X,Y) :- X1 = X - 1, breeze(X1,Y), Y1 = Y + 1, breeze(X,Y1).
pit(X,Y) :- X1 = X - 1, breeze(X1,Y), Y1 = Y - 1, breeze(X,Y1).
pit(X,Y) :- cell(X,Y), X1 = X - 1, breeze(X1,Y), X2 = X - 3, breeze(X2,Y).
pit(X,Y) :- X1 = X + 1, breeze(X1,Y), Y1 = Y + 1, breeze(X,Y1).
pit(X,Y) :- X1 = X + 1, breeze(X1,Y), Y1 = Y - 1, breeze(X,Y1).
pit(X,Y) :- cell(X,Y), X1 = X + 1, breeze(X1,Y), X2 = X + 3, breeze(X2,Y).
pit(X,Y) :- Y1 = Y - 1, breeze(X,Y1), X1 = X + 1, breeze(X1,Y).
pit(X,Y) :- Y1 = Y - 1, breeze(X,Y1), X1 = X - 1, breeze(X1,Y).
pit(X,Y) :- cell(X,Y), Y1 = Y - 1, breeze(X,Y1), Y2 = Y - 3, breeze(X,Y2).
pit(X,Y) :- Y1 = Y + 1, breeze(X,Y1), X1 = X + 1, breeze(X1,Y).
pit(X,Y) :- Y1 = Y + 1, breeze(X,Y1), X1 = X - 1, breeze(X1,Y).
pit(X,Y) :- cell(X,Y), Y1 = Y + 1, breeze(X,Y1), Y2 = Y + 3, breeze(X,Y2).

% Strategy
action(climb) :- position(1,1), breeze(1,2), breeze(2,1).
