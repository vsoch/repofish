from glob import glob
import numpy
import pickle
import os

# Run iterations of "count" to count the number of terms in each folder of zipped up pubmed articles

home = os.environ["HOME"]
scripts = "%s/SCRIPT/python/repofish/analysis/methods" %(home)
base = "%s/data/pubmed" %os.environ["LAB"]
outfolder = "%s/repos" %(base)
articles_folder = "%s/articles" %(base)

if not os.path.exists(outfolder):
    os.mkdir(outfolder)

folders = [x for x in glob("%s/*" %articles_folder) if os.path.isdir(x)]

batch_size = 1000.0
iters = int(numpy.ceil(len(folders)/batch_size))

# Prepare and submit a job for each
for i in range(iters):
    start = i*int(batch_size)
    if i != iters:
        end = start + int(batch_size)
    else:
        end = len(folders)
    subset = folders[start:end] 
    script_file = "%s/findgithub_%s.job" %(scripts,i)
    filey = open(script_file,'w')
    filey.writelines("#!/bin/bash\n")
    filey.writelines("#SBATCH --job-name=%s\n" %i)
    filey.writelines("#SBATCH --output=.out/%s.out\n" %i)
    filey.writelines("#SBATCH --error=.out/%s.err\n" %i)
    filey.writelines("#SBATCH --time=2:00:00\n")
    for folder in subset:   
        filey.writelines('python %s/1.find_repos.py "%s" %s\n' % (scripts,folder,outfolder))
    filey.close()
    os.system("sbatch -A Analysis_Lonestar -p normal findgithub_%s.job" %i)
