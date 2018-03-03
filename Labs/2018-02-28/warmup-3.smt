(declare-const b Bool)
(declare-const s Bool)
(declare-const w Bool)

(define-fun x () Bool (or (and b s) w))
(define-fun y () Bool (=> (=> b (not s)) w))

(assert (not (= x y)))
(check-sat)
