#show assign/2.

person(1..15).
location(tud).
location(fub).
location(tuw).
location(unl).

% choice(X,Y,1) first choice person X location Y. assigned with weight 4
% choice(X,Y,2) assigned with weight 2

:- choice(X, _, _), not person(X).

% Each person can select at most two locations.
:- choice(X, Y, _), choice(X, Z, _), choice(X, U, _), Y != Z, Y != U, Z != U.

% A person selects a location.
assign(X,Y) :- person(X), location(Y), choice(X,Y,_).

% :- assign(X,Y), choice(X,Y,_)

first_choice(C) :- C = #count { person(X) : assign(X,Z) , choice(X,Y,1) , Y != Z}

% #minimize {person(X), choice(X,Y,1), assign(X,Z), Y != Z}

:- 4 #count { person(X) : assign(X,tud) }.
:- 5 #count { person(X) : assign(X,fub) }.
:- 4 #count { person(X) : assign(X,tuw) }.
:- 6 #count { person(X) : assign(X,unl) }.
