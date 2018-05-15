% Result should be action(A).

% Neighboring cells along the horizontal and vertical axis.
neighbor(X1,Y1,X2,Y2) :- X2 = X + 1, Y2 = Y1.
neighbor(X1,Y1,X2,Y2) :- X2 = X, Y2 = Y1 + 1.
neighbor(X1,Y1,X2,Y2) :- X2 = X - 1, Y2 = Y1.
neighbor(X1,Y1,X2,Y2) :- X2 = X, Y2 = Y1 - 1.

danger(X,Y) :- neighbor(X,Y,X1,Y1), stench(X1,Y1), -wumpus(X1,Y1).
danger(X,Y) :- neighbor(X,Y,X1,Y1), breeze(X1,Y1), -pit(X1,Y1).

wumpus(X,Y) :- stench(X - 1, Y), stench(X, Y - 1), stench(X + 1, Y), stench(X, Y + 1).
pit(X,Y) :- breeze(X - 1, Y), breeze(X, Y - 1), breeze(X + 1, Y), breeze(X + 1, Y).
gold(X,Y) :- -gold_picked, glitter(X,Y).
