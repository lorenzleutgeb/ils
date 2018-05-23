#show assign/2.

person(1..15).
location(TUD).
location(FUB).
location(TUW).
location(UNL).

% Each person can select at most two universities.
#count { location(X) : select(_,X) } 2.
:- select(X,A), select(X,B), select(X,C), A != B, B != C, A != C.
% A person selects a location.
%select(X,Y) :- person(X), location(Y).

#count { person(X) : assign(X,TUD) } 3.
#count { person(X) : assign(X,FUB) } 4.
#count { person(X) : assign(X,TUW) } 3.
#count { person(X) : assign(X,UNL) } 5.
