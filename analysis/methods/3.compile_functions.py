from glob import glob
import pickle
import pandas
import numpy
import json
import os
import re

home = os.environ["HOME"]
base = "%s/data/pubmed" %os.environ["LAB"]
method_folder = "%s/methods" %(base)
repo_folder = "%s/repos" %(base)

methods_files = glob("%s/*.tsv" %method_folder)

# Take a look at repo urls to help parsing
methods = pandas.DataFrame()
for m in range(len(methods_files)):
    methods_file = methods_files[m]
    print "Parsing %s of %s" %(m,len(methods_files))
    result = pandas.read_csv(methods_file,sep="\t",index_col=0)
    methods = methods.append(result)

methods.to_csv("%s/pmc_functions.tsv" %base,sep="\t")
