set autoscale

unset log
unset label

set samples 10

set xtic auto
set ytic auto

set title "Average Execution Time\n (for k = 5, with 100 experiments per point)"

set xlabel "r = l / n"
set ylabel "t [ms]"

set format y "%.0s"

set terminal png size 960,540
set output "time-5.png"

# "data-3.dat" using 1:3 title 'n = 50' with linespoints , \
#set arrow from 4.25,0.001 to 4.25,0.256 nohead

set arrow from 21.25,0 to 21.25,0.9 nohead dt "."

plot "data-5.dat" using 1:3 title 'n = 50' with linespoints
