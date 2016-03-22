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
pickle.dump(targz_list,open(targz_list,"wb"))

# Write to launch file

batch_size = 500
iters = len(pc_ids)/batch_size

script_file = "%s/findgithub.job" %scripts
filey = open(script_file,'w')

for i in range(iters):
    download_subfolder = "%s/%s" %(download_folder,i)
    if not os.path.exists(download_subfolder):
        os.mkdir(download_subfolder)
    start = i*batch_size
    if i != iters:
        end = start + batch_size
    else:
        end = len(pc_ids)
    filey.writelines("python %s/count_methods.py %s %s %s %s %s\n" % (scripts,start,end,targz_list,outfolder))

filey.close()
