#show assign/2.

person(1..15).
rank(1..2).
location(tud).
location(fub).
location(tuw).
location(unl).

% Typing choice/3.
:- choice(X, _, _), not person(X).
:- choice(_, Y, _), not location(Y).
:- choice(_, _, Z), not rank(Z).
% The same choice cannot be made on two different locations.
:- choice(X,Y,Z), choice(X,W,Z), Y != W.
% Each person can select at most two locations.
:- choice(X, Y, _), choice(X, Z, _), choice(X, U, _), Y != Z, Y != U, Z != U.
% Same location for different choices of a person are ruled out.
:- choice(X,Y,1), choice(X,Y,2).

:- 4 #count { person(X) : assign(X,tud) }.
:- 5 #count { person(X) : assign(X,fub) }.
:- 4 #count { person(X) : assign(X,tuw) }.
:- 6 #count { person(X) : assign(X,unl) }.

% Each person must be assigned to a location.
1 { assign(X,Y) : location(Y) } 1 :- person(X).

% Each person must be assigned to a unique location.

% A person is assigned to a location (not necessarily a chosen one).
assign(X,Y) ; -assign(X,Y) :- person(X), location(Y).

first(C) :- C = #count { person(X) : assign(X,Y), choice(X,Y,1) }.
second(C) :- C = #count { person(X) : assign(X,Y), choice(X,Y,2) }.
bad(C) :- C = #count { person(X) : assign(X,Y), not choice(X,Y,_) }.

#maximize {4*C@3, C : first(C)}.
#maximize {2*C@2, C : second(C)}.
#maximize {0*C@1, C : bad(C)}.
