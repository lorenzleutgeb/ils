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

accept(5).
accept(6).

delta(0,a,7).
delta(0,b,1).

delta(1,a,7).
delta(1,b,0).

delta(2,a,4).
delta(2,b,5).

delta(3,a,4).
delta(3,b,6).

delta(4,a,5).
delta(4,b,6).

delta(5,a,5).
delta(5,b,5).

delta(6,a,6).
delta(6,b,5).

delta(7,a,2).
delta(7,b,2).

% Answer 1: merge(0,1) merge(2,3) merge(5,6)
