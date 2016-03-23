from repofish.pubmed import get_xml
from glob import glob
import pickle
import os

# Run iterations of "count" to count the number of terms in each folder of zipped up pubmed articles

home = os.environ["HOME"]
scripts = "%s/SCRIPT/python/repofish/analysis/methods" %(home)
base = "%s/pubmed" %os.environ["WORK"]
articles_folder = "%s/articles/13" %(base)
outfolder = "%s/repos" %(base)

if not os.path.exists(outfolder):
    os.mkdir(outfolder)

targzs = glob("%s/*.tar.gz" %articles_folder)
targz_list = "%s/targz_list.pkl" %(base)

# Save list for later
pickle.dump(targzs,open(targz_list,"wb"))

# Write to launch file
batch_size = 100
iters = len(targzs)/batch_size

script_file = "%s/findgithub.job" %scripts
filey = open(script_file,'w')

for i in range(iters):
    start = i*batch_size
    if i != iters:
        end = start + batch_size
    else:
        end = len(targzs)
    filey.writelines("python %s/find_repos.py %s %s %s %s\n" % (scripts,start,end,targz_list,outfolder))

filey.close()
