set autoscale

unset log
unset label

set samples 10

set xtic auto
set ytic auto

set ytics (0.001, 0.002)

set title "Average Execution Time\n (for k = 2, with 150 experiments per point)"

set xlabel "r = l / n"
set ylabel "t [ms]"

#set yrange [0.001:0.256]
#set logscale y 2
set format y "%.0s"

set terminal png size 960,540
set output "time-2.png"

plot "data-2.dat" using 1:3 title 'n = 20' with linespoints , \
     "data-2.dat" using 1:6 title 'n = 50' with linespoints , \
     "data-2.dat" using 1:9 title 'n = 100' with linespoints , \
     "data-2.dat" using 1:12 title 'n = 200' with linespoints , \
     "data-2.dat" using 1:15 title 'n = 500' with linespoints
