symbol(a).
symbol(b).

state(0).
state(1).
state(2).
state(3).
state(4).
state(5).

accept(1).
accept(5).

delta(0,a,1).
delta(0,b,4).

delta(1,a,2).
delta(1,b,3).

delta(2,a,2).
delta(2,b,4).

delta(3,a,2).
delta(3,b,4).

delta(4,a,5).
delta(4,b,0).

delta(5,a,3).
delta(5,b,2).

% Answer 1: merge(0,4) merge(1,5) merge(2,3)
