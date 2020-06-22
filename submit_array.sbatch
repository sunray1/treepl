#!/bin/bash

#SBATCH --array=1-100
#SBATCH --job-name=treepl   #A name for your job
#SBATCH --output=rax%A_%a.out   #Name output file
#SBATCH --mail-type=ALL   #What emails you want
#SBATCH --mail-user=###   #Where
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8   #Request a single processor
#SBATCH --mem-per-cpu=500mb   #Per processor memory request
#SBATCH --time=10:00:00   #Walltime in hh:mm:ss or d-hh:mm:ss
#SBATCH --account=###
#SBATCH --qos=###

module load treepl
module load python3


python run_treepl.py 100_trees ${SLURM_ARRAY_TASK_ID} step1_output
python run_treepl2.py 100_trees ${SLURM_ARRAY_TASK_ID} step2.1_output
python run_treepl2.py 100_trees ${SLURM_ARRAY_TASK_ID} step2.2_output
python run_treepl2.py 100_trees ${SLURM_ARRAY_TASK_ID} step2.3_output
python run_treepl3.py 100_trees ${SLURM_ARRAY_TASK_ID} step3_output
