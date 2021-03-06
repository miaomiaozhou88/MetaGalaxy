#!/usr/bin/env python3

import sys, os, glob, argparse, time, datetime, multiprocessing, threading, subprocess, logging
from Bio import SeqIO
from Bio.SeqIO.QualityIO import FastqGeneralIterator

class printblock:
	def __init__(self, *args, **kw):
		sys.stdout.flush()
		self._origstdout= sys.stdout
		self._oldstdout_fno= os.dup(sys.stdout.fileno())
		self._devnull= os.open(os.devnull, os.O_WRONLY)

	def __enter__(self):
		self._newstdout = os.dup(1)
		os.dup2(self._devnull, 1)
		os.close(self._devnull)
		sys.stdout= os.fdopen(self._newstdout, "w")

	def __exit__(self, exc_type, exc_val, exc_tb):
		sys.stdout= self._origstdout
		sys.stdout.flush()
		os.dup2(self._oldstdout_fno, 1)

def use_threads(thread_count):
	if multiprocessing.cpu_count() > thread_count:
		return thread_count
	else:
		return multiprocessing.cpu_count()

def valid(infile):
	input= glob.glob(infile)
	input= ''.join(infile)
	if len(infile) == 0:
		print("\nNo input file found. Exiting MetaGalaxy\n")
		logging.warning("No input file found. Exiting MetaGalaxy\n\n")
		sys.exit(1)
	elif len(infile) != 0:
		if os.path.exists(infile) == True:
			print("\nFound file: {fn}".format(fn= fname))
			logging.info("Found file: {fn}".format(fn= fname))
		elif os.path.exists(infile) == False:
			print("\nNo input file found. Exiting MetaGalaxy.\n")
			logging.error("No input file found. Exiting MetaGalaxy\n\n")
			sys.exit(1)
	return

def run(command):
	start= time.time()
	with printblock():
		res= os.system(command)
	if not res == 0:
		tend= int(time.time() - ttime)
		telapsed= "{:02d}:{:02d}:{:02d}".format(tend // 3600, (tend % 3600 // 60), tend % 60)
		sys.stderr.write("\nError when trying to run Metagalaxy.\nTotal time elapsed: {tl}\n".format(tl=telapsed))
		logging.critical("Error when trying to run Metagalaxy.\t\tTotal time elapsed: {tl}\n".format(tl=telapsed))
		sys.exit(1)
	return

def tknd():
	exec(open(bin+"/MG_KND.py").read());

def tkpd():
	exec(open(bin+"/MG_KPD.py").read());

def trqc():
	exec(open(bin+"/MG_RQC.py").read());

def tflr():
	exec(open(bin+"/MG_FLR.py").read());
	
def tpar():
	exec(open(bin+"/MG_PAR.py").read());

def tfqc():
	exec(open(bin+"/MG_FQC.py").read());

def tapm():
	exec(open(bin+"/MG_APM.py").read());

def taqc():
	exec(open(bin+"/MG_AQC.py").read());

def tctb():
	exec(open(bin+"/MG_CTB.py").read());

def tabr():
	exec(open(bin+"/MG_ABR.py").read());

def tbts():
	exec(open(bin+"/MG_BTS.py").read());


if __name__ == "__main__":
	__author__= "M.D.C. Jansen"
	__version__= "MetaGalaxy v2.0.0"
	__date__= "31th of January, 2020"
	done= False
	ttime= time.time()
	parser= argparse.ArgumentParser(prog="MetaGalaxy", description="MetaGalaxy is designed to identify bacteria from metagenomic samples and detect their AMR genes. It uses basecalled nanopore data in fastq format. Ensure that the conda environment is activated before using this pipeline [conda activate metagalaxy]. ", usage="%(prog)s -i <inputfile> [options]", epilog= "Thank you for using MetaGalaxy!")
	parser._optionals.title= "Arguments for Metagalaxy"
	parser.add_argument("-v", "--version", help= "Prints program version and exits Metagalaxy", action= "version", version= __version__+" "+__date__+" by "+__author__)
	parser.add_argument("-i", metavar= "[input]", help= "Input .fastq file for analysis or file directory for demultiplexing", required= "--bc_avail" not in sys.argv and len(sys.argv) != 1)
	parser.add_argument("-o", metavar= "[output]", help= "Output directory", required= False, default= "Metagalaxy_output/")
	parser.add_argument("-t", metavar= "[threads]", help= "Amount of threads [max available up to 256 threads]", required= False, type=int, default= use_threads(256))
	parser.add_argument("-g", metavar= "[gsize]", help= "Esitmated genome size [8m]", required= False, default= "8m")
	parser.add_argument("--demultiplex", metavar= '', help= "MetaGalaxy will demultiplex the files from the specified input directory and trim the barcodes", required= False, type=bool, nargs= "?", const= True, default= False)
	parser.add_argument("--bc_kit", metavar= "[]", help= "Specify the barcoding kit for demultiplexing. Only required when used in conjunction with --demultiplex", required= "--demultiplex" in sys.argv, default="")
	parser.add_argument("--bc_avail", metavar= '', help= "Prints all the available barcoding kits for demultiplexing and exits Metagalaxy", required= False, type=bool, nargs="?", const= True, default= False)
	parser.add_argument("--keep", metavar= '', help= "Keep all files produced by MetaGalaxy", required= False, type=bool, nargs= "?", const= True, default= False)
	argument= parser.parse_args()
	bin_dir = "bin"
	data_dir= "data"
	lib_dir = "lib"
	root= os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
	bin= os.path.join(root, bin_dir)
	data= os.path.join(root, data_dir)
	lib= os.path.join(root, lib_dir)
	if len(sys.argv) == 1:
		parser.print_help(sys.stderr)
		sys.exit(0)
	demultiplex= argument.demultiplex
	bckit= argument.bc_kit
	bcavail= argument.bc_avail
	if bcavail == True:
		os.system("guppy_barcoder --print_kits")
		sys.exit(0)
	infile= os.path.abspath(argument.i)
	fname= os.path.basename(argument.i)
	outdir= os.path.abspath(argument.o)
	MGlog= os.path.join(os.path.abspath(argument.o), "MetaGalaxy.log")
	if os.path.exists(outdir) == True:
		logging.basicConfig(filename=MGlog, level=logging.DEBUG, format="%(asctime)s - %(levelname)-8s - %(threadName)-10s - %(message)s")
		logging.info("MetaGalaxy initiated")
		print("\nOutput directory already exists, do you want to clear the contents of the directory?")
		logging.warning("Output directory already exists, do you want to clear the contents of the directory?")
		answer= input("[y/n]\n")
		if answer == "y" or answer == "yes" or answer == "YES" or answer == "Y":
			logging.info("Answer: Yes")
			print("\nClearing directory...", end="\r")
			logging.info("Clearing directory...")
			os.chdir(outdir)
			os.system("find . ! -name 'MetaGalaxy.log' ! -name '.' -type d -exec rm -rf {} +")
			os.system("find . ! -name 'MetaGalaxy.log' ! -name '.' ! -type d -exec rm -rf {} +")
			print("Output directory has been cleared.\n")
			logging.info("Output directory has been cleared")
		elif answer == "n" or answer == "no" or answer == "NO" or answer == "N":
			print("\nDirectory will not be cleared. Analyses resuming.\nNOTE: Existing data might be overwritten!\n")
			logging.warning("Directory will not be cleared. Analyses resuming. NOTE: Existing data might be overwritten!")
		else:
			print("\nUnknown input. Please provide a valid input (y/yes - n/no). Exiting MetaGalaxy\n")
			logging.error("Unknown input. Please provide a valid input (y/yes - n/no). Exiting MetaGalaxy\n\n")
			sys.exit(1)
	elif os.path.exists(outdir) == False:
		os.mkdir(outdir)
		logging.basicConfig(filename=MGlog, level=logging.DEBUG, format="%(asctime)s - %(levelname)-8s - %(threadName)-10s - %(message)s")
		print("\nOutput directory: {od} has been created".format(od=outdir))
		logging.info("MetaGalaxy initiated")
		logging.info("Output directory: {od} has been created".format(od=outdir))
	threads= str(argument.t)
	gsize= argument.g
	keep= argument.keep
	if demultiplex == True:
		indir= os.path.abspath(argument.i)
		logging.info("Settings MetaGalaxy:\n\nInput directory:\t\t{ind}\nOutput directory:\t{od}\nThreads:\t\t{td}\n".format(ind=indir, od=outdir, td=threads))
		exec(open(bin+"/MG_DMP.py").read());
		sys.exit(0)
	valid(infile)
	logging.info("Settings MetaGalaxy:\n\nInput file:\t\t{fn}\nOutput directory:\t{od}\nThreads:\t\t{td}\nEstimated genome size:\t{gs}\nKeep all files:\t\t{kp}\n".format(fn=fname, od=outdir, td=threads, gs=gsize, kp=keep))
	knd= threading.Thread(target= tknd)
	kpd= threading.Thread(target= tkpd)
	rqc= threading.Thread(target= trqc)
	flr= threading.Thread(target= tflr)
	par= threading.Thread(target= tpar)
	fqc= threading.Thread(target= tfqc)
	apm= threading.Thread(target= tapm)
	aqc= threading.Thread(target= taqc)
	ctb= threading.Thread(target= tctb)
	abr= threading.Thread(target= tabr)
	bts= threading.Thread(target= tbts)
	knd.start()
	kpd.start()
	rqc.start()
	flr.start()
	flr.join()
	par.start()
	fqc.start()
	knd.join()
	kpd.join()
	apm.start()
	apm.join()
	aqc.start()
	ctb.start()
	ctb.join()
	abr.start()
	abr.join()
	bts.start()
	par.join()
	rqc.join()
	fqc.join()
	aqc.join()
	bts.join()
	done= True
	tend= int(time.time() - ttime)
	telapsed= "{:02d}:{:02d}:{:02d}".format(tend // 3600, (tend % 3600 // 60), tend % 60)
	MG_end= "\nThank you for using MetaGalaxy! The analysis took {tl} to complete.".format(tl=telapsed)
	print(MG_end)
	logging.info("Completed analysis\n{mg}\n\n\n".format(mg=MG_end))
	sys.exit(0)
