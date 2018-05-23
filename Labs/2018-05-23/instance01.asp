symbol(a).
symbol(b).

state(0).
state(1).
state(2).
state(3).
state(4).

accept(4).

delta(0,a,1).
delta(0,b,2).

delta(1,a,1).
delta(1,b,3).

delta(2,a,1).
delta(2,b,2).

delta(3,a,1).
delta(3,b,4).

delta(4,a,1).
delta(4,b,2).

% Answer 1: merge(0,2)
