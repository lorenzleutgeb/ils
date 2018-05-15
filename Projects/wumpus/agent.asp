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

% Result should be action(A).

% Neighboring cells along the horizontal and vertical axis.
neighbor(X1,Y1,X2,Y2) :- cell(X1,Y1), cell(X2,Y2), X2 = X1 + 1, Y2 = Y1.
neighbor(X1,Y1,X2,Y2) :- cell(X1,Y1), cell(X2,Y2), X2 = X1, Y2 = Y1 + 1.
neighbor(X1,Y1,X2,Y2) :- cell(X1,Y1), cell(X2,Y2), X2 = X1 - 1, Y2 = Y1.
neighbor(X1,Y1,X2,Y2) :- cell(X1,Y1), cell(X2,Y2), X2 = X1, Y2 = Y1 - 1.

danger(X,Y) :- cell(X,Y), cell(X1,Y1), neighbor(X,Y,X1,Y1), stench(X1,Y1), -wumpus(X1,Y1).
danger(X,Y) :- cell(X,Y), cell(X1,Y1), neighbor(X,Y,X1,Y1), breeze(X1,Y1), -pit(X1,Y1).

wumpus(X,Y) :- X1 = X - 1, stench(X1, Y), Y1 = Y - 1, stench(X, Y1), X2 = X + 1, stench(X2, Y), Y2 = Y + 1, stench(X, Y2).
pit(X,Y) :- X1 = X - 1, breeze(X1, Y), Y1 = Y - 1, breeze(X, Y1), X2 = X + 1, breeze(X2, Y), Y2 = Y + 1, breeze(X, Y2).
%gold(X,Y) :- -gold_picked, glitter(X,Y).
