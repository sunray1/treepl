#! /usr/bin/env python

import sys, os

mkdircommd = "mkdir %s/%s"
cpconfig = "cp treepl_step1.config %s/%s"
sandr = "sed -i 's/%s/%s/g' %s"
runtreepl = "treePL %s > %s"
mvcmnd = "mv %s %s"
#./prog.py tree_directory num out_dir
#num starts with 1
args = sys.argv
tree_directory = args[1]
num = args[2]
outdir = args[3]

tree_files = os.listdir(tree_directory)
ind_tree_file = tree_files[int(num)-1]
ind_tree_suff = ind_tree_file.split("tree")[1].split(".")[0]

os.system(mkdircommd % (outdir, ind_tree_suff))
os.system(cpconfig % (outdir, ind_tree_suff))

os.system(sandr % ("treefile =", "treefile = " + tree_directory + "\/" + ind_tree_file, outdir + "/" + ind_tree_suff + "/" + "treepl_step1.config"))
os.system(sandr % ("outfile =", "outfile = " + outdir + "\/" + ind_tree_suff + "\/doesntmatter.tre", outdir + "/" + ind_tree_suff + "/" + "treepl_step1.config"))
os.system(runtreepl % (outdir + "/" + ind_tree_suff + "/" + "treepl_step1.config", outdir + "/" + ind_tree_suff + "/tree" + ind_tree_suff + "_step1.out"))
os.system(mvcmnd % (outdir + "/" + ind_tree_suff + "/tree" + ind_tree_suff + "_step1.out", outdir))