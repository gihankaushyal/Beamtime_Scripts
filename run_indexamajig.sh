#!/bin/sh

#SBATCH --array 0-4
#SBATCH --job-name PS2-S4-%a
#SBATCH --output S4/stdout-%a.log
#SBATCH --error S4/stderr-%a.log
#SBATCH --time 180
#SBATCH --partition htc
#SBATCH -c 64
#SBATCH --qos public 
##SBATC --qos grp_cxfel
#SBATCH --nodes 1
#SBATCH --mail-type FAIL
#SBATCH --nice=100

~/Software/crystfel-v0.11.1/bin/indexamajig -i input_files/S4-files.lst${SLURM_ARRAY_TASK_ID} -g shift4-finalAug2022.geom -o S4/crystfel-${SLURM_ARRAY_TASK_ID}.stream -j `nproc` --peaks=peakfinder8 --threshold=800 --min-peaks=10 --min-snr=6 --min-pix-count=2 --max-pix-count=20 --local-bg-radius=3 --min-res=60 --max-res=250 --peak-radius=2.0,4.0,6.0 --indexing=mosflm,mosflm-nocell,mosflm-nolatt,xds,taketwo,xgandalf -p crystal.cell --tolerance=10,10,10,5,5,5 --multi --check-peaks --refine --integration=rings --int-radius=2.0,4.0,6.0 --fix-divergence=0.000000 --serial-start=$((${SLURM_ARRAY_TASK_ID}*1000+1))
