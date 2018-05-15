#maxint = 100.

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


% Cells that are in front of the agent.

facing(X,Y) :- position(X,Z), Z < Y, orientation(right).
facing(X,Y) :- position(X,Z), Y < Z, orientation(left).
facing(X,Y) :- position(Z,Y), Z < X, orientation(up).
facing(X,Y) :- position(Z,Y), X < Z, orientation(down).

% Result should be action(A).

% Pick gold if there's some in the cell.
action(grab) :- position(X,Y), gold(X,Y).
% Cannot pick up something that's already been picked!
% TODO: how to remove gold from knowledge once it's been collected?
%       SOLUTION: at next call, add -gold(X,Y) to KB.
:- gold(X,Y), position(X,Y), gold_picked.
% When to shoot at the wumbus?
action(shoot) :- wumpus(X,Y), facing(X,Y).
% Climb if gold is picked and back to initial cell.
action(climb) :- gold_picked, position(1,1).

% Neighboring cells along the horizontal and vertical axis.
neighbor(X1,Y1,X2,Y2) :- cell(X1,Y1), cell(X2,Y2), X2 = X1 + 1, Y2 = Y1.
neighbor(X1,Y1,X2,Y2) :- cell(X1,Y1), cell(X2,Y2), X2 = X1, Y2 = Y1 + 1.
neighbor(X1,Y1,X2,Y2) :- cell(X1,Y1), cell(X2,Y2), X2 = X1 - 1, Y2 = Y1.
neighbor(X1,Y1,X2,Y2) :- cell(X1,Y1), cell(X2,Y2), X2 = X1, Y2 = Y1 - 1.

danger(X,Y) :- cell(X,Y), cell(X1,Y1), neighbor(X,Y,X1,Y1), stench(X1,Y1), -wumpus(X1,Y1).
danger(X,Y) :- cell(X,Y), cell(X1,Y1), neighbor(X,Y,X1,Y1), breeze(X1,Y1), -pit(X1,Y1).

% To detect the wumpus, we just need to find 2 stenches out of 4.
wumpus(X,Y) :- X1 = X - 1, stench(X1,Y), Y1 = Y + 1, stench(X,Y1).
wumpus(X,Y) :- X1 = X - 1, stench(X1,Y), Y1 = Y - 1, stench(X,Y1).
wumpus(X,Y) :- X1 = X - 1, stench(X1,Y), X2 = X - 3, stench(X2,Y).
wumpus(X,Y) :- X1 = X + 1, stench(X1,Y), Y1 = Y + 1, stench(X,Y1).
wumpus(X,Y) :- X1 = X + 1, stench(X1,Y), Y1 = Y - 1, stench(X,Y1).
wumpus(X,Y) :- X1 = X + 1, stench(X1,Y), X2 = X + 3, stench(X2,Y).
wumpus(X,Y) :- Y1 = Y - 1, stench(X,Y1), X1 = X + 1, stench(X1,Y).
wumpus(X,Y) :- Y1 = Y - 1, stench(X,Y1), X1 = X - 1, stench(X1,Y).
wumpus(X,Y) :- Y1 = Y - 1, stench(X,Y1), Y2 = Y - 3, stench(X,Y2).
wumpus(X,Y) :- Y1 = Y + 1, stench(X,Y1), X1 = X + 1, stench(X1,Y).
wumpus(X,Y) :- Y1 = Y + 1, stench(X,Y1), X1 = X - 1, stench(X1,Y).
wumpus(X,Y) :- Y1 = Y + 1, stench(X,Y1), Y2 = Y + 3, stench(X,Y2).

% To detect a pit, we just need to find 2 breezes out of 4.
pit(X,Y) :- X1 = X - 1, breeze(X1,Y), Y1 = Y + 1, breeze(X,Y1).
pit(X,Y) :- X1 = X - 1, breeze(X1,Y), Y1 = Y - 1, breeze(X,Y1).
pit(X,Y) :- X1 = X - 1, breeze(X1,Y), X2 = X - 3, breeze(X2,Y).
pit(X,Y) :- X1 = X + 1, breeze(X1,Y), Y1 = Y + 1, breeze(X,Y1).
pit(X,Y) :- X1 = X + 1, breeze(X1,Y), Y1 = Y - 1, breeze(X,Y1).
pit(X,Y) :- X1 = X + 1, breeze(X1,Y), X2 = X + 3, breeze(X2,Y).
pit(X,Y) :- Y1 = Y - 1, breeze(X,Y1), X1 = X + 1, breeze(X1,Y).
pit(X,Y) :- Y1 = Y - 1, breeze(X,Y1), X1 = X - 1, breeze(X1,Y).
pit(X,Y) :- Y1 = Y - 1, breeze(X,Y1), Y2 = Y - 3, breeze(X,Y2).
pit(X,Y) :- Y1 = Y + 1, breeze(X,Y1), X1 = X + 1, breeze(X1,Y).
pit(X,Y) :- Y1 = Y + 1, breeze(X,Y1), X1 = X - 1, breeze(X1,Y).
pit(X,Y) :- Y1 = Y + 1, breeze(X,Y1), Y2 = Y + 3, breeze(X,Y2).

wumpus(X,Y) :- X1 = X - 1, stench(X1, Y), Y1 = Y - 1, stench(X, Y1), X2 = X + 1, stench(X2, Y), Y2 = Y + 1, stench(X, Y2).
pit(X,Y) :- X1 = X - 1, breeze(X1, Y), Y1 = Y - 1, breeze(X, Y1), X2 = X + 1, breeze(X2, Y), Y2 = Y + 1, breeze(X, Y2).
%gold(X,Y) :- -gold_picked, glitter(X,Y).
