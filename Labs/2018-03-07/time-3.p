set autoscale

unset log
unset label

set samples 10

set xtic auto
set ytic auto

set ytics (0.001, 0.002, 0.004, 0.008, 0.016, 0.032, 0.064, 0.128, 0.256)

set title "Average Execution Time\n (for k = 3, with 100 experiments per point)"

set xlabel "r = l / n"
set ylabel "t [ms]"

set yrange [0.001:0.256]
set logscale y 2
set format y "%.0s"

set terminal png size 960,540
set output "time-3.png"

# "data-3.dat" using 1:3 title 'n = 50' with linespoints , \

set arrow from 4.29,0.001 to 4.29,0.256 nohead

plot "data-3.dat" using 1:6 title 'n = 100' with linespoints , \
     "data-3.dat" using 1:9 title 'n = 200' with linespoints

set arrow from 3, graph 0 to 4.25, graph 1 nohead
