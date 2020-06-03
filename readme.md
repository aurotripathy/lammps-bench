You need to install in the same directory as the LAMMPS benchmarks

<code>
git clone https://github.com/aurotripathy/lammps-bench.git .
</code>

How to run

<code>
python2.7 lammps-bench2-geo-mean.py -f 3.1GHz -c 36 -t 2
</code>

or

<code>
python2.7 lammps-bench2-geo-mean.py --freq-str 3.1GHz --core-count-list 36 --thread-count 2
</code>