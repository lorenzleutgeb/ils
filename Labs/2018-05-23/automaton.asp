#show merge/2.

% symbol/1, state/1, accept/1, delta/3

% Condition 1
distinguish(Q1, Q2) :-
	    accept(Q1),
	    state (Q2),
	not accept(Q2).

% Condition 2
distinguish(Q1, Q2) :-
	delta(Q1, A, Sx),
	delta(Q2, A, Sy),
	distinguish(Sx, Sy),
	Q1 != Q2.

% Symmetry
distinguish(Q1, Q2) :-
	distinguish(Q2, Q1).

% Closedness
-distinguish(Q1, Q2) :-
	    state(Q1),
	    state(Q2),
	not distinguish(Q1, Q2).

% Transitivity
-distinguish(Q1, Q3) :-
	-distinguish(Q1, Q2),
	-distinguish(Q2, Q3).

merge(Q1, Q2) :-
	state(Q2),
	Q1 = #min{Q3: -distinguish(Q3, Q2)},
	Q1 != Q2.
