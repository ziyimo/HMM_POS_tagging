#!/bin/bash
#
#SBATCH --verbose
#SBATCH --job-name=HMM_POS_tagging
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err
#SBATCH --time=05:00:00
#SBATCH --nodes=4
#SBATCH --mem=32GB

module purge
module load python3/intel/3.5.3

./Viterbi_tagger.py WSJ_POS_CORPUS_FOR_STUDENTS/WSJ_full.pos WSJ_POS_CORPUS_FOR_STUDENTS/WSJ_23.words zm561_WSJ_23_sys.pos

exit
