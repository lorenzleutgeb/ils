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
state(8).
state(9).

accept(1).
accept(2).
accept(3).
accept(5).
accept(6).

delta(0,a,1).
delta(0,b,2).

delta(1,a,3).
delta(1,b,4).

delta(2,a,5).
delta(2,b,6).

delta(3,a,3).
delta(3,b,8).

delta(4,a,6).
delta(4,b,7).

delta(5,a,7).
delta(5,b,0).

delta(6,a,1).
delta(6,b,4).

delta(7,a,7).
delta(7,b,9).

delta(8,a,6).
delta(8,b,9).

delta(9,a,9).
delta(9,b,7).

% Answer 1: merge(1,3) merge(1,6) merge(4,8) merge(7,9)
