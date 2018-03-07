set autoscale

unset log
unset label

set xtic auto
set ytic auto

set title "Phase Transition"

set xlabel "r"
set ylabel "p"

set terminal png
set output "satisfiability.png"

plot "satisfiability.dat" using 1:2 title  '50' with linespoints , \
     "satisfiability.dat" using 1:3 title '100' with points , \
     "satisfiability.dat" using 1:4 title '200' with points
