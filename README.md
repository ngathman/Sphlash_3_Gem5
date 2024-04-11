# Splash_3_Gem5

codes/ directory contains the compiled Splash 3 benchmarks. The source code comes from the following repository https://github.com/SakalisC/Splash-3 with the citation below.  If you make changes to the source code, you must recompile by calling "make" in the /codes directory
  

Prior to this work, there was already a python run file, run.py, for Splash under configs/splash2. This python file contained non-existent root paths to the benchmarks and did not support a Ruby system. The SPEC benchmark python file spec_se.py under configs/spec did support using a Ruby system. Thus, the changes in run.py are a combination of spec_se.py and run.py.

Place codes/ wherever you see fit, but update the variable $BASEDIR in codes/Makefile.config to point to where codes/ is located in the Gem5 hierarchy. Currently I have codes/ located in the home directory of Gem5 (where you compile from), so the Makefile.config is configured for that location. 

I encountered fopen errors while debugging, so if you encounter an error related to "Error opening a file" check the following. 
1) Check the file exists. If the error does not say which file, trace the error and print the path. Ensure the path matches how it should be refrerred to from the executing directory (executing directory may not be the Gem5 home directory, check by printing out the executing path from where the opening error occurs).
2) Check permissions of the file for reading
3) If the file does not exist, it is possible the code is trying to open an invalid input file. If this is the case, check the run.py benchmark class and verify the input file name matches an input file in codes/{apps,kernel}/{benchmark name}. Note: the -p at the end of the input file represents the number of processors
 
The results are stored in m5out/stat.txt

To run a benchmark, use the following example that runs Barnes.
build/ECE666/gem5.opt configs/splash2/run.py -b Barnes -n 4

To run the benchmark with traces, add --debug-flags=ProtocolTrace after gem5.opt. Beware, the trace will increase simulation time. 


Splash 3 Source code citation

C. Sakalis, C. Leonardsson, S. Kaxiras, and A. Ros, “Splash-3: A
properly synchronized benchmark suite for contemporary research,”
in Performance Analysis of Systems and Software (ISPASS), 2016
IEEE International Symposium On, IEEE, 2016.
