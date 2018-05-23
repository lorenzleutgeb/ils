symbol(a).
symbol(b).

state(0).
state(1).
state(2).
state(3).
state(4).
state(5).
state(6).
state(7).

accept(2).

delta(0,a,1).
delta(0,b,5).

delta(1,a,6).
delta(1,b,2).

delta(2,a,0).
delta(2,b,3).

delta(3,a,2).
delta(3,b,6).

delta(4,a,7).
delta(4,b,5).

delta(5,a,2).
delta(5,b,6).

delta(6,a,6).
delta(6,b,4).

delta(7,a,6).
delta(7,b,2).

% Answer 1: merge(0,4) merge(1,7) merge(3,5)
