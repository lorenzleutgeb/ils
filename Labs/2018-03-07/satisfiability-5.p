set autoscale

unset log
unset label

set tics font ", 12"

set xtic 0.5
set mxtics 2
set ytic 0.25
set mytics 2

set title "Satisfiability\n (for k = 5, with 100 experiments per point)"

set xlabel "r = l / n"
set ylabel "p"

set terminal png size 960,540
set output "satisfiability-5.png"

#set arrow from 4.25,0 to 4.25,1 nohead dt "."
set arrow from 19,0.5 to 25,0.5 nohead dt "."
set arrow from 21.25,0 to 21.25,1 nohead dt "."

plot "data-5.dat" using 1:2 title 'n = 50' with linespoints
