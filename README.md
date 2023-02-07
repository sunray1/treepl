## 1. Get bootstrap alignments

Need:
* Alignment
* Partitioning Scheme (if using)

-f j: Command to create bootstrapped alignment files

-m: Model (is not used here, but is required to let command run)

-s: Alignment

-q: Partition file (RAxML cannot use different models per partition, but will infer different rates per partition)

-n: name appended to output files

-b: seed

-#: Number of replicates

-T: Number of threads to use

```
raxmlHPC-PTHREADS-SSE3 -f j -m GTRGAMMAI -s $Alignment_file -q $Partition_file -n BS -T $Num_of_Threads -# 100 -b $RANDOM
```
## 2. Add branch lengths to tree given bootstrap alignment

Need:
 * Tree with arbitrary branch lengths (final tree topology)
 * Alignments from Step 1
 
 If you have a tree with branch lengths or bootstraps you can use the following command to remove numbers, colons and periods from your file:
 ```
 sed -r 's/[0-9:.]//g' input.tre > output_topo.tre
```
 
 
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

**Note: Testing this now: Not sure if there is a diff between R and FigTree rooting**

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

To do this in phyx (seems better):
```
module load gcc/8.2.0
module load phyx/20190403
pxrr -t RAxML_bootstrap.bootstrap_all.tre -g GCA_0003309851_Plutella_xylostella -o RAxML_bootstrap.bootstrap_all_rooted.tre
```
## 4. Run TreePL on each tree

Need:

* Tree file with rooted bootstrap trees
* Skeleton config files for each step
* Python wrapper script for each step
* Output directories for each step

### Step 4.0

Make a directory that will house all individual files. This is so we can run them in parallel.
```
mkdir 100_trees
split -l 1 RAxML_bootstrap.bootstrap_all_rooted.tre 100_trees/RAxML_bestTree.MLone_tree
for i in 100_trees/*; do mv $i $i.tre; done
```
### Step 4.1 Run treepl

First, go ahead and edit the skeleton config files and the sbatch file where there are 'xxx' to match your data. Specifically, this includes-

In the .config files:
* numsites
* mrca for each constraint
* min for each constraint
* max for each constraint

In the .sbatch file:
* mail-user
* account and qos

The sbatch file will run the priming step (step 1), cv step (step 2), and dating step (step 3) for each tree file in order. In this example, I date 100 trees, but this can be increased or decreased if you'd like. The sbatch file is an array, so all 100 trees are submitted to run in parallel. The time and memory can be changed as well, as well as any other parameters in the config files (threads, cv, etc). Feel free to comment out steps and run them one at a time if you'd like.

By default, I chose to run the cv (step 2) step 3 times, but this can be increased in the sbatch file (just make sure the corresponding output directory is also created). I then choose the best smoothing parameter for each run based on the lowest chisq value and choose the most common value out of the three runs. If all three runs show different values, I choose the smoothing parameter that has the lowest chisq value across all three runs.

Make sure to chmod the python scripts! Also - the jobs may come back with a FAILED status when nothing actually failed. Check the config and output files in each step - there should be 100 directories in each output and 100 .out files in each of the directories as well. 

```
sbatch submit_array.sbatch
```
## 5. Summarize trees with treeAnnotator
```
cd step3_output
cat *.tre > treeall_dated.tre
module load beast
treeannotator
```
