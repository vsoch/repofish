from glob import glob
import pandas
import numpy
import pickle

input_folder = "/share/PI/russpold/work/PUBMED/fmri/counts"
output_folder = "/share/PI/russpold/work/PUBMED/fmri"
files = glob("%s/*.pkl" %input_folder)
tmp = pickle.load(open(files[0],"rb"))

# Save counts dataframe, total words, and missing
counts = pandas.DataFrame(columns=tmp["df"].columns)
total_words = []
files_in_folder = []
noterms_count = []

# Function to Save to file
def save_result(counts,total_words,files_in_folder,noterms_count):
    pickle.dump(noterms_count,open("%s/fmri_noterms.pkl" %output_folder,"wb"))
    pickle.dump(files_in_folder,open("%s/fmri_files.pkl" %output_folder,"wb"))
    pickle.dump(total_words,open("%s/fmri_totalwords.pkl" %output_folder,"wb"))
    pickle.dump(counts,open("%s/fmri_counts.pkl" %output_folder,"wb"))


for f in range(0,len(files)):
    print "%s of %s" %(f,len(files))
    input_folder = files[f]
    count = pickle.load(open(input_folder,"rb"))
    counts = counts.append(count["df"])
    total_words.append(count["total_words"])
    files_in_folder.append(count["files_in_folder"])
    noterms_count.append(count["noterms_count"])
    if f % 1000 == 0:
        save_result(counts,total_words,files_in_folder,noterms_count)

save_result(counts,total_words,files_in_folder,noterms_count)


