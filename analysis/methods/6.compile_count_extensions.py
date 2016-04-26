from glob import glob
import pandas
import numpy
import pickle
import os

home = os.environ["HOME"]
base = "%s/DATA/PUBMED" %os.environ["SCRATCH"]
counts_folder = "%s/counts" %(base)

files = glob("%s/*.tsv" %counts_folder)

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

# Filter out people's jobfiles (error and output)
colnames = [x for x in colnames if not re.search("[.]o[0-9]+",x)]
colnames = [x for x in colnames if not re.search("[.]e[0-9]+",x)]

# Save a data frame of counts
counts = pandas.DataFrame(columns=colnames)

for f in files:
    entry = os.path.basename(f).replace("extcounts.tsv","").split("_")
    pmid = entry[0]
    user_name = entry[1]
    repo_name = "".join(entry[2:])
    uid = "%s_%s" %(user_name,repo_name)
    result = pandas.read_csv(f,index_col=0,sep="\t")
    counts.loc[uid,result.index] = result["count"]
    if uid in repos:
        repos[uid].append(pmid)
    else:
        repos[uid] = [pmid]

counts.to_csv("%s/extension_counts.tsv" %base,sep="\t")
pickle.dump(repos,open("%s/extension_repos.pkl","wb"))
