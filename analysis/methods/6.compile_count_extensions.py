from glob import glob
import pandas
import numpy
import pickle
import os
import re

home = os.environ["HOME"]
base = "%s/DATA/PUBMED" %os.environ["SCRATCH"]
counts_folder = "%s/counts" %(base)

files = glob("%s/*.tsv" %counts_folder)
len(files)
#4660

# save a lookup to associate repos with pmids, if there are repeats
repos = dict()

# First let's get unique columns
colnames = []
for f in files:
    entry = os.path.basename(f).replace("extcounts.tsv","").split("_")
    pmid = entry[0]
    user_name = entry[1]
    repo_name = "".join(entry[2:])
    uid = "%s_%s" %(user_name,repo_name)
    result = pandas.read_csv(f,index_col=0,sep="\t")
    colnames = numpy.unique([colnames + result.index.tolist()]).tolist()

# Note that we will want to combine counts for job files (.o[number] and .e[number])
colnames = [x for x in colnames if not re.search("[.]o[0-9]+",x)]
colnames = [x for x in colnames if not re.search("[.]e[0-9]+",x)]
colnames = colnames + ["JOBFILE_OUTPUT","JOBFILE_ERROR"]
len(colnames)
#4611

# Save a data frame of counts
counts = pandas.DataFrame(columns=colnames)

# A function to find output / error files, return updated result object
def find_job_files(result):
    error_files = [x for x in result.index if re.search("[.]e[0-9]+",x)]
    output_files = [x for x in result.index if re.search("[.]o[0-9]+",x)]
    if len(error_files)>0:
        error_count = result.loc[error_files].sum()["count"]
        result = result.drop(error_files)
        result.loc["JOBFILE_ERROR"] = error_count
    if len(output_files)>0:
        output_count = result.loc[output_files].sum()["count"]
        result = result.drop(output_files)
        result.loc["JOBFILE_OUTPUT"] = output_count
    return result


for f in range(len(files)):
    print "Parsing %s of %s" %(f,len(files))
    filey = files[f]
    entry = os.path.basename(filey).replace("extcounts.tsv","").split("_")
    pmid = entry[0]
    user_name = entry[1]
    repo_name = "".join(entry[2:])
    uid = "%s_%s" %(user_name,repo_name)
    result = pandas.read_csv(filey,index_col=0,sep="\t")
    # Find output and error files
    result = find_job_files(result)
    counts.loc[uid,result.index] = result["count"]
    if uid in repos:
        repos[uid].append(pmid)
    else:
        repos[uid] = [pmid]

counts.to_csv("%s/extension_counts.tsv" %base,sep="\t")
pickle.dump(repos,open("%s/extension_repos.pkl","wb"))
