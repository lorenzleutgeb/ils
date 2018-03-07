set autoscale

unset log
unset label

set xtic auto
set ytic auto

set title "Execution Time"

set xlabel "r"
set ylabel "t [s]"

set terminal png
set output "time.png"

plot "data.dat" using 1:3 title  '50' with points , \
     "data.dat" using 1:5 title '100' with points , \
     "data.dat" using 1:7 title '200' with points
