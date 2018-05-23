state(0).
state(1).
state(2).
state(3).
state(4).
state(5).
state(6).

accept(1).
accept(5).
accept(6).

symbol(a).
symbol(b).

delta(0,a,1).
delta(2,a,3).
delta(4,a,4).
delta(6,a,5).
delta(0,b,4).
delta(2,b,5).
delta(4,b,6).
delta(6,b,6).
delta(1,a,2).
delta(3,a,2).
delta(5,a,5).
delta(1,b,4).
delta(3,b,6).
delta(5,b,6).

% Answer 1: merge(2,3) merge(2,4) merge(5,6)
