% NOTE: Should correspond to wumpus.common.Orientation
#const right = 0.
#const up    = 1.
#const left  = 2.
#const down  = 3.

isOrientation(0..3).

% NOTE: Should correspond to wumpus.common.Action
#const goforward = 0.
#const turnleft  = 1.
#const turnright = 2.
#const grab      = 3.
#const shoot     = 4.
#const climb     = 5.

isAction(0..5).

% NOTE: Should correspond to wumpus.agent.Mode
#const explore = 0.
#const escape  = 1.
#const kill    = 2.

isMode(0..2).
