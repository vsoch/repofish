from glob import glob
import json
import pandas
import requests
import numpy
import pickle
import os
import re

# FOR RUNNING ON TACC WITH LAUNCH (fails to clone at once) ######################################## 
home = os.environ["HOME"]
base = "%s/data/pubmed" %os.environ["LAB"]
outfolder = "%s/methods" %(base)
repo_folder = "%s/repos" %(base)
scripts = "%s/SCRIPT/repofish/analysis/methods" %(home)
counts_folder = "%s/counts" %(base)

if not os.path.exists(counts_folder):
    os.mkdir(counts_folder)

urls = pickle.load(open("%s/inputs_categorized.pkl" %outfolder,"rb"))["repos"]
len(urls)
#5570

jobfile = "%s/count_extensions.job" %(scripts)
filey = open(jobfile,"w")

for entry in urls:
    pmid = entry[0]
    url = entry[1]
    filey.writelines("python %s/5.count_extensions.py %s %s %s\n" %(scripts,pmid,url,counts_folder))

filey.close()
    
# FOR RUNNING ON SHERLOCK ######################################################################## 
home = os.environ["HOME"]
base = "%s/DATA/PUBMED" %os.environ["SCRATCH"]
outfolder = "%s/methods" %(base)
scripts = "%s/SCRIPT/python/repofish/analysis/methods" %(home)
counts_folder = "%s/counts" %(base)

if not os.path.exists(counts_folder):
    os.mkdir(counts_folder)

urls = pickle.load(open("%s/inputs_categorized.pkl" %outfolder,"rb"))["repos"]
len(urls)
#5570

count=0
for entry in urls:
    pmid = entry[0]
    url = entry[1]
    job_id = "%s_%s" %(pmid,count)
    jobfile = "%s/.job/%s.job" %(scripts,job_id)
    filey = open(jobfile,"w")
    filey.writelines("#!/bin/bash\n")
    filey.writelines("#SBATCH --job-name=%s\n" %(job_id))
    filey.writelines("#SBATCH --output=.out/%s.out\n" %(job_id))
    filey.writelines("#SBATCH --error=.out/%s.err\n" %(job_id))
    filey.writelines("#SBATCH --time=30:00\n")
    filey.writelines("#SBATCH --mem=4000\n")
    filey.writelines("python %s/5.count_extensions.py %s %s %s\n" %(scripts,pmid,url,counts_folder))
    filey.close()
    os.system("sbatch -p russpold --qos=russpold " + "%s/.job/%s.job" %(scripts,job_id))
    count+=1

