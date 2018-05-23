#show merge/2.

% Basic criterion.
distinguish(S1,S2) :- accept(S1), state(S2), not accept(S2).
distinguish(S1,S2) :- delta(S1,A,Sx), delta(S2,A,Sy), Sx != Sy.

% Recursive criterion.
%-distinguish(S1,S3) :- state(S1), state(S2), state(S3), S1 < S2, S2 < S3, not distinguish(S1,S2), not distinguish(S2,S3).
%-distinguish(S1,S2) :- state(S1), state(S2), not distinguish(S1,S2).

merge(S1,S2) :- state(S1), state(S2), S1 < S2, not distinguish(S1,S2).
