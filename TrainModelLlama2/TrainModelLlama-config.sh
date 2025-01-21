#!/bin/bash

#SBATCH --job-name=trainModelLlama
#SBATCH --output=trainModelLlama_output_%j.out
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --partition=gpu

python3 TrainModelLlama.py
