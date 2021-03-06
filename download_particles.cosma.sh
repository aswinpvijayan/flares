#!/bin/bash
#SBATCH --ntasks 16
#SBATCH -A dp004
#SBATCH -p cosma7
#SBATCH --job-name=get_FLARES
#SBATCH --array=0-39%10
#SBATCH -t 0-1:30
###SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=8
#SBATCH -o logs/std_output.%J
#SBATCH -e logs/std_error.%J

module purge
module load gnu_comp/7.3.0 openmpi/3.0.1 hdf5/1.10.3 python/3.6.5

#arg1 is the region number (in case of FLARES, leave it as some number for periodic boxes), arg2 is the relevant tag (snap number), arg3 is FLARES/REF/AGNdT9, arg4 is the text file with the relevant arrys to be written into the hdf5 file and agr5 is the folder you want the files to be saved
#In case of Periodic boxes, set the ntasks number to a cube to make a proper division of the box


source ./venv_fl/bin/activate

### For FLARES galaxies, change ntasks as required
array=(011_z004p770 010_z005p000 009_z006p000 008_z007p000 007_z008p000 006_z009p000 005_z010p000 004_z011p000 003_z012p000 002_z013p000 001_z014p000 000_z015p000)


for ii in ${array[@]}
  do
    mpiexec -n 16 python3 -m mpi4py download_methods.py $SLURM_ARRAY_TASK_ID $ii FLARES data3
    python3 write_req_arrs.py $SLURM_ARRAY_TASK_ID $ii FLARES data3 req_arrs.txt
done

### For PERIODIC boxes: REF and AGNdT9, change ntasks and time as required (REF at z=5 required ~1.hr)
# Apparently choosing something higher than 27 is under-reprting the number of galaxies for some reason,
# needs investigation -- later
# array=(002_z009p993 003_z008p988 004_z008p075 005_z007p050 006_z005p971 008_z005p037)
# array=(010_z003p984 011_z003p528)
# array=(012_z003p017)
#
# for ii in ${array[@]}
#   do
#     mpiexec -n 27 python3 -m mpi4py download_methods.py 0 $ii REF ./
#     python3 write_req_arrs.py 0 $ii REF ./ req_arrs.txt
# done

echo "Job done, info follows..."
sacct -j $SLURM_JOBID --format=JobID,JobName,Partition,MaxRSS,Elapsed,ExitCode
exit
