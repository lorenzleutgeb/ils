set autoscale

unset log
unset label

set tics font ", 12"

set xtic 0.25
set mxtics 2
set ytic 0.25
set mytics 2

set title "Satisfiability\n (for k = 2, with 150 experiments per point)"

set xlabel "r = l / n"
set ylabel "p"

set terminal png size 960,540
set output "satisfiability-2.png"

#set arrow from 4.25,0 to 4.25,1 nohead dt "."
set arrow from 0.25,0.5 to 3.25,0.5 nohead dt "."
set arrow from 4.29,0 to 4.29,1 nohead dt "."

# 20, 50, 100, 200, 500

plot "data-2.dat" using 1:2 title 'n = 20' with linespoints , \
     "data-2.dat" using 1:5 title 'n = 50' with linespoints , \
     "data-2.dat" using 1:8 title 'n = 100' with linespoints , \
     "data-2.dat" using 1:11 title 'n = 200' with linespoints , \
     "data-2.dat" using 1:14 title 'n = 500' with linespoints
