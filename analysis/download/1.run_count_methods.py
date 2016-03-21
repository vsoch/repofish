from glob import glob
import os

# Run iterations of "count" to count the number of terms in each folder of zipped up pubmed articles

topfolder = "/scratch/PI/russpold/data/PUBMED/articles"
subfolders = [os.path.basename(x) for x in glob("%s/*" %topfolder)]
outfolder = "/share/PI/russpold/work/PUBMED/fmri/counts"

# This pickle has a list of our terms
term_pickle =  "/home/vsochat/SCRIPT/brainbehavior/brainbehavior/data/fmri.pkl"
folders = subfolders[:]
count = 0

while len(folders)>0:
    subfolder = folders[0]
    queue_count = int(os.popen("squeue -u vsochat | wc -l").read().strip("\n"))
    if queue_count < 1000:
        if not os.path.exists("%s/%s_counts.pkl" %(outfolder,subfolder)):
            jobfile = open(".job/%s.job" %subfolder,'w')
            jobfile.writelines("#!/bin/bash\n")
            jobfile.writelines("#SBATCH --job-name=%s_count.job\n" %(subfolder))
            jobfile.writelines("#SBATCH --output=.out/%s_count.out\n" %(subfolder))
            jobfile.writelines("#SBATCH --error=.out/%s_count.err\n" %(subfolder)) 
            jobfile.writelines("#SBATCH --time=2-00:00\n") 
            jobfile.writelines("#SBATCH --mem=12000\n")   
            jobfile.writelines("python /home/vsochat/SCRIPT/brainbehavior/analysis/fmri/1.count_fmri.py %s %s %s %s\n" %(topfolder,subfolder,term_pickle,outfolder))  
            jobfile.close()
            os.system('sbatch -p russpold .job/%s.job' %subfolder)
        folders.pop(0) 
