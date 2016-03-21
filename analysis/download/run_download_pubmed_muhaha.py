#!/usr/bin/env python2

# This script will launch instances of download_pubmed_muhaha.py

from repofish.pubmed import load_pmc
import pickle
import os

base = "/scratch/PI/russpold/data/PUBMED"
base = "/work/02092/vsochat/pubmed"

# Save the pickled ftp and pmcids
ftp_pickle = "%s/ftp_df.pkl" %(base)
ftp = load_pmc()
pickle.dump(ftp,open(ftp_pickle,"wb"))

ids_pickle = "%s/pmc_ids.pkl" %(base)
pc_ids = list(ftp["PMCID"])
pickle.dump(pc_ids,open(ids_pickle,"wb"))
#pc_ids = pickle.load(open(ids_pickle,"rb"))

# Submit scripts to download in batches of 450
batch_size = 500
iters = len(pc_ids)/batch_size

# We will download them here
download_folder = "%s/articles" %(base)

if not os.path.exists(download_folder):
    os.mkdir(download_folder)

# SHERLOCK
# Prepare and submit a job for each
for i in range(iters):
    download_subfolder = "%s/%s" %(download_folder,i)
    if not os.path.exists(download_subfolder):
        os.mkdir(download_subfolder)
    start = i*batch_size
    if i != iters:
        end = start + batch_size
    else:
        end = len(pc_ids)
    jobname = "pm_%s-%s" %(start,end)
    filey = open(".job/%s.job" % (jobname),"w")
    filey.writelines("#!/bin/bash\n")
    filey.writelines("#SBATCH --job-name=%s\n" %(jobname))
    filey.writelines("#SBATCH --output=.out/%s.out\n" %(jobname))
    filey.writelines("#SBATCH --error=.out/%s.err\n" %(jobname))
    filey.writelines("#SBATCH --time=2-00:00\n")
    filey.writelines("#SBATCH --mem=12000\n")
    filey.writelines("python /home/vsochat/SCRIPT/python/repofish/analysis/download/download_pubmed_muhaha.py %s %s %s %s %s\n" % (start,end,download_subfolder,ftp_pickle,ids_pickle))
    filey.close()
    os.system("sbatch -p russpold --qos russpold .job/%s.job" % (jobname))


# TACC
homebase = "%s/SCRIPT/python/repofish/analysis/download" %os.environ["HOME"]
output_file = "%s/pmclaunch.job" %homebase
filey = open(output_file,"w")

# Prepare and submit a job for each
for i in range(iters):
    download_subfolder = "%s/%s" %(download_folder,i)
    if not os.path.exists(download_subfolder):
        os.mkdir(download_subfolder)
    start = i*batch_size
    if i != iters:
        end = start + batch_size
    else:
        end = len(pc_ids)
    filey.writelines("python %s/download_pubmed_muhaha.py %s %s %s %s %s\n" % (homebase,start,end,download_subfolder,ftp_pickle,ids_pickle))

filey.close()
