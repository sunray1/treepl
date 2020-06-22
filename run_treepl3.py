#! /usr/bin/env python

import sys, os, statistics
import pandas as pd

getfirstline = "grep -n 'PLACE THE LINES' %s"
getlastline = "wc -l %s"
getlinestoadd = "sed -n '%s,%sp' %s"

mkdircommd = "mkdir %s/%s"
cpconfig = "cp treepl_step3.config %s/%s"
sandr = "sed -i 's/%s/%s/g' %s"
sandr_first = "sed -i '0,/%s/{s/%s/%s/}' %s"
runtreepl = "treePL %s"
mvcmnd = "mv %s %s"
lsstep2 = "ls step2*"

#./prog.py tree_directory num out_dir
#num starts with 1
args = sys.argv
tree_directory = args[1]
num = args[2]
outdir = args[3]

#get treesuffix
tree_files = os.listdir(tree_directory)
ind_tree_file = tree_files[int(num)-1]
ind_tree_suff = ind_tree_file.split("tree")[1].split(".")[0]

#make tree directory and cp config file over
os.system(mkdircommd % (outdir, ind_tree_suff))
os.system(cpconfig % (outdir, ind_tree_suff))

#edit config file
os.system(sandr % ("treefile =", "treefile = ..\/..\/" + tree_directory + "\/" + ind_tree_file, outdir + "/" + ind_tree_suff + "/" + "treepl_step3.config"))
os.system(sandr % ("outfile =", "outfile = tree" + ind_tree_suff + "_dated.tre", outdir + "/" + ind_tree_suff + "/" + "treepl_step3.config"))

#get prime lines
firstline = os.popen(getfirstline % ("step1_output/tree" + ind_tree_suff + "_step1.out")).read()
startnum = int(firstline.split(":")[0]) + 1
lastline = os.popen(getlastline % ("step1_output/tree" + ind_tree_suff + "_step1.out")).read()
endnum = lastline.split()[0]

primeadd = os.popen(getlinestoadd % (str(startnum), endnum, "step1_output/tree" + ind_tree_suff + "_step1.out"))
for i in primeadd:
	os.system(sandr_first % ("# ", "# ", i.strip(), outdir + "/" + ind_tree_suff + "/" + "treepl_step3.config"))
	
#get smoothing parameter	
step2dirs = [filename for filename in os.listdir('.') if filename.startswith("step2")]
chisqs = []
logl = []
for i in step2dirs:
	outfile = i + "/tree" + ind_tree_suff + ".out"
	df = pd.read_csv(outfile,sep=' ', header = None, names=['xx', 'chisq', 'logl'])
	min_index = list(df['logl']).index(min(df['logl']))
	min_logl = float(df['logl'][min_index])
	min_chisq = list(df['chisq'])[min_index]
	min_chisq = float(min_chisq.strip(")").strip("("))
	chisqs.append(min_chisq)
	logl.append(min_logl)

try:
	#got the lowest chisq from each run, pick the most
	mode = statistics.mode(chisqs)
	os.system(sandr % ("smooth =", "smooth = " + str(mode), outdir + "/" + ind_tree_suff + "/" + "treepl_step3.config"))
	os.chdir(outdir + "/" + ind_tree_suff)
	os.system(runtreepl % ("treepl_step3.config"))
	os.system(mvcmnd % ("tree"+ ind_tree_suff + "_dated.tre", "../" + "tree"+ind_tree_suff+"_dated.tre"))
	
except:
	#if there isn't one most common, pick the one with the lowest likelihood
	all_logl_min = min(logl)
	min_index = logl.index(all_logl_min)
	min_chisq = chisqs[min_index]
	os.system(sandr % ("smooth =", "smooth = " + str(min_chisq), outdir + "/" + ind_tree_suff + "/" + "treepl_step3.config"))
	os.chdir(outdir + "/" + ind_tree_suff)
	os.system(runtreepl % ("treepl_step3.config"))
	os.system(mvcmnd % ("tree"+ ind_tree_suff + "_dated.tre", "../" + "tree"+ind_tree_suff+"_dated.tre"))

