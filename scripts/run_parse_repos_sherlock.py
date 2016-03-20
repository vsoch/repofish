import pickle
import pandas
import os

# This doesn't matter, function will clone repos locally if doesn't work
access_token = "vanessavanessavanessa"

# Read in list of Github repos
base = "/scratch/PI/russpold/data/PUBMED"
repos_folder = "%s/repos" %(base)
output_folder = "%s/functions" %(repos_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# This is a list of repos parsed from pubmed
repos_file = "%s/repos_github_pandas_df.pkl" %(repos_folder)
repos = pickle.load(open(repos_file,"rb"))

seen = []
for row in repos.iterrows():
    pubmed_paper = row[1].journals
    repo_url = row[1].urls
    if repo_url not in seen:
        print "Parsing %s" %(repo_url)
        seen.append(repo_url)
        repo_name = repo_url.split("/")[-1]
        user_name = repo_url.split("/")[-2]
        output_file = "%s/%s_%s_functions.pkl" %(output_folder,user_name,repo_name)
        if not os.path.exists(output_file):
            job_id = "%s_%s" %(user_name,repo_name)
            filey = ".job/repo_%s.job" %(job_id)
            filey = open(filey,"w")
            filey.writelines("#!/bin/bash\n")
            filey.writelines("#SBATCH --job-name=%s\n" %(job_id))
            filey.writelines("#SBATCH --output=.out/%s.out\n" %(job_id))
            filey.writelines("#SBATCH --error=.out/%s.err\n" %(job_id))
            filey.writelines("#SBATCH --time=2-00:00\n")
            filey.writelines("#SBATCH --mem=64000\n")
            filey.writelines("python parse_repos_sherlock.py %s %s %s %s" %(access_token, repo_url, output_file, pubmed_paper))
            filey.close()
            os.system("sbatch -p russpold --qos russpold " + ".job/repo_%s.job" %(job_id))
