from repofish.pubmed import get_xml
from glob import glob
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

# Write to launch file
script_file = "%s/findgithub.job" %scripts
filey = open(script_file,'w')

for folder in folders:
    filey.writelines("python %s/1.find_repos.py %s %s\n" % (scripts,folder,outfolder))

filey.close()
