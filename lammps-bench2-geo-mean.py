# from https://janakiev.com/blog/python-shell-commands/
# Must use pyhton2.7
import os, stat
import subprocess
import math
import argparse
import time

def set_freq(freq):
   """ 
   note, freq is a string
   substitute the freq in the list of commands below 
   """
   command_list = """
   echo "toor" | sudo -S /sbin/modprobe cpufreq_userspace
   echo "toor" | sudo -S sudo /usr/bin/cpupower frequency-set --governor userspace
   echo "toor" | sudo -S sudo /usr/bin/cpupower --cpu all frequency-set --freq {} 
   cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq
   """.format(freq)

   print(command_list)

   p = subprocess.Popen(command_list, stdout=subprocess.PIPE, shell=True)

   (output, err) = p.communicate()
   p_status = p.wait()

   #This will give you the output of the command being executed
   print "Command output: " + output

   output_lines = output.splitlines()
   print(output_lines)


def nth_root(num,root):
   return num ** (1/root)

def geo_mean(nums):
    product = 1
    for num in nums:
        product *= num
    return(nth_root(product, float(len(nums))))


def replace_core_count_n_thread_count(freq_str, core_count, thread_count):
   out_lines = []
   with open('./run_benchmarks.sh', 'r') as in_file :
      for line in in_file:

         if line.startswith('export LMP_CORES='):
            out_lines.append('export LMP_CORES=' + str(core_count) + '\n')
         elif line.startswith('export LMP_THREAD_LIST='):
            out_lines.append('export LMP_THREAD_LIST=' + '"{}"'.format(thread_count) + '\n')
         else:
            out_lines.append(line)
            
   out_file_name = '/tmp/run_benchmarks_' + 'freq_' + freq_str + \
                   '_core_count' + '_' + str(core_count) + \
                   '_t_count_' + thread_count + '.sh'
   print('name', out_file_name)
   with open(out_file_name, 'w') as out_file :
         out_file.writelines(out_lines)
   os.chmod(out_file_name, 0o777)
   return(out_file_name)


parser = argparse.ArgumentParser(description='Automation for collecting LAMMPS data')
parser.add_argument('-c', '--core-count-list', nargs="+", type=int,
                    required=True, help="List of core counts that will be used one by one.")
parser.add_argument('-t', '--thread-count', type=str,
                    required=True, help="OMP threads")
parser.add_argument('-f', '--freq_str', type=str,
                    required=True, help="CPU freq in MHz, all cores")

args = parser.parse_args()

print('core count list', args.core_count_list)

for core_count in args.core_count_list:
   print('Using freq', args.freq_str)
   set_freq(args.freq_str)
   out_file_name = replace_core_count_n_thread_count(args.freq_str, core_count, args.thread_count)

   print('Writing new core-count', core_count, 'and thread', args.thread_count,
         ' to:', out_file_name)

   process = subprocess.Popen([out_file_name], 
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              universal_newlines=True)
   collect_output = []

   (output, err) = process.communicate()

   #This makes the wait possible
   p_status = process.wait()
   
   #This will give you the output of the command being executed
   print("Command output: \n" + output)

   collect_output = output.splitlines()


   # Collect lines that begin with the benchmark names
   # Perf is not a benchmark; its an artifact of how the resuts are presented.
   # If you are doing one benchmark, then the preface is 'Perfformance', else its the name of the benchmark
   bench_list = ['lj', 'rhodo', 'lc', 'sw', 'water', 'eam', 'airebo', 'dpd', 'tersoff', 'Perf']
   bench_numbers = []
   # print('Benchmarks:')
   for line in collect_output:
      if list(filter(line.startswith, bench_list)) != []:
         bench_numbers.append(float(line.split()[1]))
       # for bench in bench_list:
       #     if bench in line[:10]:
       #         bench_numbers.append(float(line.split()[1]))
       #         # print(line.strip())
   print('Taking the geometric mean of:', bench_numbers)
   print('Core count:', core_count, 'Geo mean:', geo_mean(bench_numbers))
