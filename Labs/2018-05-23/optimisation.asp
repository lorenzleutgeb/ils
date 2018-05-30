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
0 { choice(X,Y,Z) : location(Y) } 1 :- person(X), rank(Z).
% Same location for different choices of a person are ruled out.
:- choice(X,Y,1), choice(X,Y,2).

% Each person can select at most two locations.
0 { choice(X,Y,Z) : location(Y), rank(Z) } 2 :- person(X).

0 { assign(X,tud) : person(X) } 3.
0 { assign(X,fub) : person(X) } 4.
0 { assign(X,tuw) : person(X) } 3.
0 { assign(X,unl) : person(X) } 5.

% Each person must be assigned to a unique location.
1 { assign(X,Y) : location(Y) } 1 :- person(X).

% A person is assigned to a location (not necessarily a chosen one).
assign(X,Y) ; -assign(X,Y) :- person(X), location(Y).

first(C) :- C = #count { person(X) : assign(X,Y), choice(X,Y,1) }.
second(C) :- C = #count { person(X) : assign(X,Y), choice(X,Y,2) }.
bad(C) :- C = #count { person(X) : assign(X,Y), not choice(X,Y,_) }.

#maximize {4*C@3, C : first(C)}.
#maximize {2*C@2, C : second(C)}.
#minimize {0*C@1, C : bad(C)}.
