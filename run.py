# Copyright (c) 2005-2007 The Regents of The University of Michigan
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Splash2 Run Script
#
# Edited by Nicole Gathman to support Ruby systems 
# Edits are a combination of spec_se.py (for Ruby setup) and this splash run.py file as is


import os
import argparse
import sys

import m5
from m5.defines import buildEnv
from m5.objects import *
from m5.params import NULL
from m5.util import addToPath, fatal, warn

addToPath('../')

from ruby import Ruby

from common import Options
from common import Simulation
from common import CacheConfig
from common import CpuConfig
from common import ObjectList
from common import MemConfig
from common.FileSystemConfig import config_filesystem
from common.Caches import *
from common.cpu2000 import *




# --------------------
# Define Command Line Options
# ====================

parser = argparse.ArgumentParser()
Options.addCommonOptions(parser)
Options.addSEOptions(parser)

# Add Ruby options
Ruby.define_options(parser)

parser.add_argument("-d", "--detailed", action="store_true")
parser.add_argument("-t", "--timing", action="store_true")
parser.add_argument("-f", "--frequency",
                    default = "1GHz",
                    help="Frequency of each CPU")
parser.add_argument("--l1size",
                    default = "32kB")
parser.add_argument("--l1latency",
                    default = "1ns")
parser.add_argument("--l2size",
                    default = "256kB")
parser.add_argument("--l2latency",
                    default = "10ns")
parser.add_argument("--rootdir",
                    help="Root directory of Splash2",
                    default="codes")
parser.add_argument("-b", "--benchmark",
                    help="Splash 2 benchmark to run")

args = parser.parse_args()

if not args.num_cpus:
    print("Specify the number of cpus with -n")
    sys.exit(1)


#------------------
# Nicole: Removed clock frequency from input because it caused an error
#------------------

busFrequency = Frequency(args.frequency)

if args.timing:
    cpus = [TimingSimpleCPU(cpu_id = i)
            for i in range(args.num_cpus)]
elif args.detailed:
    cpus = [DerivO3CPU(cpu_id = i,
                       clock=args.frequency)
            for i in range(args.num_cpus)]
else: #default to timing because Atomic has atomic memory instructions which is not suitable for caching
    cpus = [TimingSimpleCPU(cpu_id = i)
            for i in range(args.num_cpus)]


np = args.num_cpus
numThreads = 1
(CPUClass, test_mem_mode, FutureClass) = Simulation.setCPUClass(args)
CPUClass.numThreads = numThreads
system = System(cpu = cpus,
                mem_mode = test_mem_mode,
                mem_ranges = [AddrRange(args.mem_size)],
                cache_line_size = args.cacheline_size)

if numThreads > 1:
    system.multi_thread = True

# --------------------
# Define Splash2 Benchmarks
# ====================
class Cholesky(Process):
    cwd = args.rootdir + '/kernels/cholesky'
    executable = args.rootdir + '/kernels/cholesky/CHOLESKY'
    cmd = ['CHOLESKY', '-p' +  str(args.num_cpus),
            'inputs/tk23.O']

class FFT(Process):
    cwd = args.rootdir + '/kernels/fft'
    executable = args.rootdir + '/kernels/fft/FFT'
    cmd = ['FFT', '-p', str(args.num_cpus), '-m18']

class LU_contig(Process):
    executable = args.rootdir + '/kernels/lu/contiguous_blocks/LU'
    cmd = ['LU', '-p', str(args.num_cpus)]
    cwd = args.rootdir + '/kernels/lu/contiguous_blocks'

class LU_noncontig(Process):
    executable = args.rootdir + '/kernels/lu/non_contiguous_blocks/LU'
    cmd = ['LU', '-p', str(args.num_cpus)]
    cwd = args.rootdir + '/kernels/lu/non_contiguous_blocks'

class Radix(Process):
    executable = args.rootdir + '/kernels/radix/RADIX'
    cmd = ['RADIX', '-n524288', '-p', str(args.num_cpus)]
    cwd = args.rootdir + '/kernels/radix'

class Barnes(Process):
    executable = args.rootdir + '/apps/barnes/BARNES'
    cmd = ['BARNES']
    input = args.rootdir + '/apps/barnes/inputs/n8k-p' + str(args.num_cpus) #you can also choose another input file name n16384, look in barnes/inputs/ for other input files
    cwd = args.rootdir + '/apps/barnes'

class FMM(Process):
    executable = args.rootdir + '/apps/fmm/FMM'
    cmd = ['FMM']
    #if str(args.num_cpus) == '1':
        #input = args.rootdir + '/apps/fmm/inputs/input.2048'
    #else:
    input = args.rootdir + '/apps/fmm/inputs/input.'+str(args.num_cpus)+'.2048' 
    cwd = args.rootdir + '/apps/fmm'

class Ocean_contig(Process):
    executable = args.rootdir + '/apps/ocean/contiguous_partitions/OCEAN'
    cmd = ['OCEAN', '-p', str(args.num_cpus)]
    cwd = args.rootdir + '/apps/ocean/contiguous_partitions'

class Ocean_noncontig(Process):
    executable = args.rootdir + '/apps/ocean/non_contiguous_partitions/OCEAN'
    cmd = ['OCEAN', '-p', str(args.num_cpus)]
    cwd = args.rootdir + '/apps/ocean/non_contiguous_partitions'

class Raytrace(Process):
    executable = args.rootdir + '/apps/raytrace/RAYTRACE'
    cmd = ['RAYTRACE', '-p' + str(args.num_cpus),
           'inputs/teapot.env']
    cwd = args.rootdir + '/apps/raytrace'

class Water_nsquared(Process):
    executable = args.rootdir + '/apps/water-nsquared/WATER-NSQUARED'
    cmd = ['WATER-NSQUARED']
    #if args.num_cpus==1:
        #input = args.rootdir + '/apps/water-nsquared/input'
    #else:
    input = args.rootdir + '/apps/water-nsquared/inputs/n512-p' + str(args.num_cpus)
    cwd = args.rootdir + '/apps/water-nsquared'

class Water_spatial(Process):
    executable = args.rootdir + '/apps/water-spatial/WATER-SPATIAL'
    cmd = ['WATER-SPATIAL']
    #if args.num_cpus==1:
        #input = args.rootdir + '/apps/water-spatial/input'
    #else:
    input = args.rootdir + '/apps/water-spatial/inputs/n512-p' + str(args.num_cpus)
    cwd = args.rootdir + '/apps/water-spatial'

# --------------------
# Base L1 Cache Definition
# ====================

#class L1(Cache):
#    latency = args.l1latency
#    mshrs = 12
#    tgts_per_mshr = 8
#
## ----------------------
## Base L2 Cache Definition
## ----------------------
#
#class L2(Cache):
#    latency = args.l2latency
#    mshrs = 92
#    tgts_per_mshr = 16
#    write_buffers = 8



# --------------------------
# Nicole: Instantiate Ruby system for protocol alterations
# Also add necessary voltage and clock domains for the Ruby system
#---------------------------

# Create a top-level voltage domain
system.voltage_domain = VoltageDomain(voltage = args.sys_voltage)
# Create a CPU voltage domain
system.cpu_voltage_domain = VoltageDomain()
# Create a source clock for the system and set the clock period
system.clk_domain = SrcClockDomain(clock =  args.sys_clock,
                                   voltage_domain = system.voltage_domain)

# Create a separate clock domain for the CPUs
system.cpu_clk_domain = SrcClockDomain(clock = args.cpu_clock,
                                       voltage_domain =
                                       system.cpu_voltage_domain)
for cpu in system.cpu:
    cpu.clk_domain = system.cpu_clk_domain

Ruby.create_system(args, False, system)
assert(args.num_cpus == len(system.ruby._cpu_ports))
system.ruby.clk_domain = SrcClockDomain(clock = args.ruby_clock,
                                        voltage_domain = system.voltage_domain)
for i in range(np):
    ruby_port = system.ruby._cpu_ports[i]
    # Create the interrupt controller and connect its ports to Ruby
    # Note that the interrupt controller is always present but only
    # in x86 does it have message ports that need to be connected
    system.cpu[i].createInterruptController()
    # Connect the cpu's cache ports to Ruby
    ruby_port.connectCpuPorts(system.cpu[i])

# ----------------------
# Define the root
# ----------------------

root = Root(full_system = False, system = system)

# --------------------
# Pick the correct Splash2 Benchmarks
# ====================
if args.benchmark == 'Cholesky':
    root.workload = Cholesky()
elif args.benchmark == 'FFT':
    root.workload = FFT()
elif args.benchmark == 'LUContig':
    root.workload = LU_contig()
elif args.benchmark == 'LUNoncontig':
    root.workload = LU_noncontig()
elif args.benchmark == 'Radix':
    root.workload = Radix()
elif args.benchmark == 'Barnes':
    root.workload = Barnes()
elif args.benchmark == 'FMM':
    root.workload = FMM()
elif args.benchmark == 'OceanContig':
    root.workload = Ocean_contig()
elif args.benchmark == 'OceanNoncontig':
    root.workload = Ocean_noncontig()
elif args.benchmark == 'Raytrace':
    root.workload = Raytrace()
elif args.benchmark == 'WaterNSquared':
    root.workload = Water_nsquared()
elif args.benchmark == 'WaterSpatial':
    root.workload = Water_spatial()
else:
    print("The --benchmark environment variable was set to something "
          "improper. Use Cholesky, FFT, LUContig, LUNoncontig, Radix, "
          "Barnes, FMM, OceanContig, OceanNoncontig, Raytrace, WaterNSquared, "
          "or WaterSpatial", file=sys.stderr)
    sys.exit(1)

# --------------------
# Assign the workload to the cpus
# ====================
##print(args.num_cpus)
for cpu in cpus:
    cpu.workload = root.workload
    cpu.createThreads() #ISA error without this call

system.workload = SEWorkload.init_compatible(root.workload.executable)

# ----------------------
# Run the simulation
# ----------------------

#if args.timing or args.detailed:    
root.system.mem_mode = 'timing'

# instantiate configuration
m5.instantiate()

# simulate until program terminates
#print("Max tick = " + str(m5.MaxTick))
exit_event = m5.simulate(m5.MaxTick) 


print('Exiting @ tick', m5.curTick(), 'because', exit_event.getCause())

