## 1. Get bootstrap alignments

Need:
* Alignment
* Partitioning Scheme (if using)
raxmlHPC-PTHREADS-SSE3 -f j -m GTRGAMMAI -s FcC_supermatrix_round1remove_synsfixed_round3remove.fa -q partitioning_scheme.txt -n ML${SLURM_ARRAY_TASK_ID} -T 16 -# 100 -b $RANDOM
## 2. Add branch lengths to tree given bootstrap alignment

Need:
 * Tree without branch lengths (final tree topology)
 * Alignments from Step 1
 
 I used an array to run 10 runs of 10 trees in parallel on the cluster
```
#SBATCH --array=0-9

for i in {1..10};
do TASK=$(expr $i + ${SLURM_ARRAY_TASK_ID} \* 10 - 1);
raxmlHPC-PTHREADS-SSE3 -f e -t tree7_ntdegen_6part.iqtree_rooted_topology.tre -m GTRGAMMAI -s out.NTDegen.fasta.reduced.BS$TASK -q best_scheme.txt.reduced.BS$TASK -n ML$TASK -T 16;
done

cat RAxML_result.ML* > RAxML_bootstrap.bootstrap_all.tre
```
## 3. Reroot all trees using R

Need:

* Concatenated tree file containing all bootstrap trees

I reroot based on tip label names - the trees are rooted to the clade
```"Papilionidae"
library(ape)
tree <- read.tree("RAxML_bootstrap.bootstrap_all.tre")
tips = tree[[1]]$tip.label
labels <- c("Papilionidae")
tip_sub <- tips[grep(labels[1], tips)]

rootedtree <- root(tree, outgroup = tip_sub, resolve.root = TRUE)
write.tree(rootedtree, file = "RAxML_bootstrap.bootstrap_all_rooted.tre")
```
## 4. Run TreePL on each tree

https://github.com/blackrim/treePL/issues/30
https://github.com/blackrim/treePL/issues/40
https://github.com/blackrim/treePL/issues/24

Output dirs need to be made,
Skeleton config files need to be made

Need:

* Tree file with rooted bootstrap trees
* Skeleton config files for each step
* Python wrapper script for each step

### Step 4.0

Make a directory that will house all indicidual files. This is so we can run them in parallel.
```
mkdir 100_trees
split -l 1 RAxML_bootstrap.bootstrap_all_rooted.tre 100_trees/RAxML_bestTree.MLone_tree
for i in 100_trees/*; do mv $i $i.tre; done
```
### Step 4.1 (prime)

--Skeleton config file--

--treepl_step1.config--
```
#tree must be in newick file and rooted correctly
treefile =
#number of sites in the alignment
numsites = 12361
#set dates
mrca = PAPILIONIDAE Papilionidae_Baronia_brevicornis Papilionidae_Battus_lycidas
min = PAPILIONIDAE 61.9
max = PAPILIONIDAE 130.7
mrca = HESPERIIDAE Hesperiidae_Phanus_marshalli Hesperiidae_Cyclosemia_anastomosis
min = HESPERIIDAE 55.6
max = HESPERIIDAE 106.7
mrca = PIERIDAE Pieridae_Eurema_agave Pieridae_Dismorphia_amphione
min = PIERIDAE 65.3
max = PIERIDAE 127.4
mrca = RIODINIDAE Riodinidae_Apodemia_nais Riodinidae_Euselasia_regipennis
min = RIODINIDAE 51.7
max = RIODINIDAE 101
mrca = LYCAENIDAE Lycaenidae_Nesiostrymon_calchinia Lycaenidae_Iophanus_pyrrhias
min = LYCAENIDAE 57.4
max = LYCAENIDAE 110
mrca = NYMPHALIDAE Nymphalidae_Argynnis_diana Nymphalidae_Mechanitis_menapis
min = NYMPHALIDAE 68.6
max = NYMPHALIDAE 130.6
outfile =
nthreads = 8
#it says using thorough makes it take longer but for my dataset it really wasn't that long of a wait
thorough
prime
```
--Python wrapper script--

--run_treepl.py--
```
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
Ran on cluster using an array to run 100 trees in parallel
#SBATCH --array=1-100

mkdir step1_output
python run_treepl.py 100_trees ${SLURM_ARRAY_TASK_ID} step1_output
rm *.out
```
### Step 4.2 (cv)

--Skeleton config file--

--treepl_step2.config--
```
treefile =
numsites = 12361
mrca = PAPILIONIDAE Papilionidae_Baronia_brevicornis Papilionidae_Battus_lycidas
min = PAPILIONIDAE 61.9
max = PAPILIONIDAE 130.7
mrca = HESPERIIDAE Hesperiidae_Phanus_marshalli Hesperiidae_Cyclosemia_anastomosis
min = HESPERIIDAE 55.6
max = HESPERIIDAE 106.7
mrca = PIERIDAE Pieridae_Eurema_agave Pieridae_Dismorphia_amphione
min = PIERIDAE 65.3
max = PIERIDAE 127.4
mrca = RIODINIDAE Riodinidae_Apodemia_nais Riodinidae_Euselasia_regipennis
min = RIODINIDAE 51.7
max = RIODINIDAE 101
mrca = LYCAENIDAE Lycaenidae_Nesiostrymon_calchinia Lycaenidae_Iophanus_pyrrhias
min = LYCAENIDAE 57.4
max = LYCAENIDAE 110
mrca = NYMPHALIDAE Nymphalidae_Argynnis_diana Nymphalidae_Mechanitis_menapis
min = NYMPHALIDAE 68.6
max = NYMPHALIDAE 130.6
outfile =
nthreads = 8
thorough
#next three lines are the results from my prime analysis
# 
# 
# 
# 
# 
# 
# 
#do cross validation to choose an ideal smoothing parameter - choose the one with the lowest chi-sq value in the cv.out file
#run this step a couple times to make sure you get the same smoothing value
#this step takes the longest (few hours), so I suggest doing this one on the cluster
cv
randomcv
#you can change these values
cvstart = 100
cvstop = .00000001
cvmultstep = 0.1
```
--Python wrapper script--

--run_treepl2.py--
```
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
Ran on cluster using an array to run 100 trees in parallel. This can be run multiple times to get consistent low parameter results for each tree (ie 2.1, 2.2 etc)
#SBATCH --array=1-100

mkdir step2.1_output
python run_treepl2.py 100_trees ${SLURM_ARRAY_TASK_ID} step2.1_output
rm *.out
```
### Step 4.3 (date)

--Skeleton config file--

--treepl_step3.config--
```
treefile =
numsites = 12361
smooth =
mrca = PAPILIONIDAE Papilionidae_Baronia_brevicornis Papilionidae_Battus_lycidas
min = PAPILIONIDAE 61.9
max = PAPILIONIDAE 130.7
mrca = HESPERIIDAE Hesperiidae_Phanus_marshalli Hesperiidae_Cyclosemia_anastomosis
min = HESPERIIDAE 55.6
max = HESPERIIDAE 106.7
mrca = PIERIDAE Pieridae_Eurema_agave Pieridae_Dismorphia_amphione
min = PIERIDAE 65.3
max = PIERIDAE 127.4
mrca = RIODINIDAE Riodinidae_Apodemia_nais Riodinidae_Euselasia_regipennis
min = RIODINIDAE 51.7
max = RIODINIDAE 101
mrca = LYCAENIDAE Lycaenidae_Nesiostrymon_calchinia Lycaenidae_Iophanus_pyrrhias
min = LYCAENIDAE 57.4
max = LYCAENIDAE 110
mrca = NYMPHALIDAE Nymphalidae_Argynnis_diana Nymphalidae_Mechanitis_menapis
min = NYMPHALIDAE 68.6
max = NYMPHALIDAE 130.6
outfile =
nthreads = 8
thorough
#next three lines are the results from my prime analysis
# 
# 
# 
# 
# 
# 
# 
```
--Python wrapper script--

--run_treepl3.py--
```
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
```

Ran on cluster using an array to run 100 trees in parallel.
```
#SBATCH --array=1-100

mkdir step3_output
python run_treepl3.py 100_trees ${SLURM_ARRAY_TASK_ID} step3_output
rm *.out
```
## 5. Summarize trees with treeAnnotator
```
cd step3_output
module load beast
treeannotator
```