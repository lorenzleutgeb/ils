set autoscale

unset log
unset label

set tics font ", 12"

#set xtic 0.25
#set mxtics 2
#set ytic 0.25
#set mytics 2

set title "Decisions\n (for k = 3, with 100 experiments per point)"

set xlabel "r = l / n"
set ylabel "p"

set logscale y 10

set terminal png size 960,540
set output "decision-3.png"

#set arrow from 4.25,0 to 4.25,1 nohead dt "."
#set arrow from 3,0.5 to 5.5,0.5 nohead dt "."
#set arrow from 4.29,0 to 4.29,1 nohead dt "."

plot "data-3.dat" using 1:4 title 'n = 50' with linespoints , \
     "data-3.dat" using 1:7 title 'n = 100' with linespoints , \
     "data-3.dat" using 1:10 title 'n = 200' with linespoints
