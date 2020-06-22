#! /usr/bin/env python

import sys, os

getfirstline = "grep -n 'PLACE THE LINES' %s"
getlastline = "wc -l %s"
getlinestoadd = "sed -n '%s,%sp' %s"

mkdircommd = "mkdir %s/%s"
cpconfig = "cp treepl_step2.config %s/%s"
sandr = "sed -i 's/%s/%s/g' %s"
sandr_first = "sed -i '0,/%s/{s/%s/%s/}' %s"
runtreepl = "treePL %s"
mvcmnd = "mv %s %s"

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
os.system(sandr % ("treefile =", "treefile = ..\/..\/" + tree_directory + "\/" + ind_tree_file, outdir + "/" + ind_tree_suff + "/" + "treepl_step2.config"))
os.system(sandr % ("outfile =", "outfile = doesntmatter.tre", outdir + "/" + ind_tree_suff + "/" + "treepl_step2.config"))
#get prime lines
firstline = os.popen(getfirstline % ("step1_output/tree" + ind_tree_suff + "_step1.out")).read()
startnum = int(firstline.split(":")[0]) + 1
lastline = os.popen(getlastline % ("step1_output/tree" + ind_tree_suff + "_step1.out")).read()
endnum = lastline.split()[0]

primeadd = os.popen(getlinestoadd % (str(startnum), endnum, "step1_output/tree" + ind_tree_suff + "_step1.out"))
for i in primeadd:
	os.system(sandr_first % ("# ", "# ", i.strip(), outdir + "/" + ind_tree_suff + "/" + "treepl_step2.config"))

#runtreepl
os.chdir(outdir + "/" + ind_tree_suff)

os.system(runtreepl % ("treepl_step2.config"))
os.system(mvcmnd % ("cv.out", "../tree" + ind_tree_suff + ".out"))