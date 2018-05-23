symbol(a).
symbol(b).

state(0).
state(1).
state(2).
state(3).

accept(2).
accept(3).

delta(0,a,1).
delta(0,b,2).

delta(1,a,0).
delta(1,b,3).

delta(2,a,2).
delta(2,b,3).

delta(3,a,2).
delta(3,b,2).

% Answer 1: merge(0,1) merge(2,3)
