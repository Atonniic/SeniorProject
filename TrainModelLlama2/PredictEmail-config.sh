#!/bin/bash

#SBATCH --job-name=predictEmail
#SBATCH --output=predictEmail_output_%j.out
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --partition=gpu

python3 PredictEmail.py
