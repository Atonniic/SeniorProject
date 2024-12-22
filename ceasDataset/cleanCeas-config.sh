#!/bin/bash

#SBATCH --job-name=cleanCeas
#SBATCH --output=cleanCeas_output_%j.out
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --partition=gpu

python cleanCeas.py
