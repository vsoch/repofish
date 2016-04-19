from glob import glob
import json
import pandas
import requests
import numpy
import pickle
import os
import re

home = os.environ["HOME"]
base = "%s/data/pubmed" %os.environ["LAB"]
outfolder = "%s/methods" %(base)
repo_folder = "%s/repos" %(base)
scripts = "%s/SCRIPT/python/repofish/analysis/methods" %(home)

if not os.path.exists(outfolder):
    os.mkdir(outfolder)

files = glob("%s/*.json" %repo_folder)

# Take a look at repo urls to help parsing
urls = []
pmids = []
for f in files:
    print "Adding %s to list" %(f)
    result = json.load(open(f,'r'))
    pubmed_paper = str(result["pmid"])
    urls = urls + result["github"]
    pmids = pmids + [pubmed_paper] * len(result["github"])

# How many?
len(numpy.unique(pmids))
# 4240
len(urls)
# 6135

# Save to inputs file
inputs = dict()
inputs["urls"] = urls
inputs["pmids"] = pmids
pickle.dump(inputs,open("%s/inputs.pkl" %outfolder,"wb"))

# inputs = pickle.load(open("%s/inputs.pkl" %outfolder,"rb"))

# Zip together
inputs = zip(inputs["pmids"],inputs["urls"])

# Remove links that are just to github
inputs = [x for x in inputs if not re.search("[http|https]://github.com$",x[1])]
inputs = [x for x in inputs if not re.search("[http|https]://www.github.com$",x[1])]

# Find urls that don't match pattern github.com/user/repo
needs_curation = [x for x in inputs if not re.search("[http|https]://(www.)?github.com/.*/.*$",x[1])]
inputs = [x for x in inputs if re.search("[http|https]://(www.)?github.com/.*/.*$",x[1])]

# We will need to parse links based on type
raw_files = []
gists = []
github_io = []
github_io_master = []
rest = []
nbviewer = []
users = []
github_help = []

while len(needs_curation) > 0:
    element = needs_curation.pop()
    # We've found a gist
    if re.search("[http|https]://gist.github.com/.*$",element[1]):
    #    print "GIST: %s" %element[1]
        gists.append(element)
    # Github help
    elif re.search("[http|https]://help.github.com/.*$",element[1]):
        github_help.append(element)
    # Github user main pages
    elif re.search("[http|https]://github.com/.*$",element[1]):
        users.append(element)
    # nbviewer
    elif re.search("nbviewer",element[1]):
        nbviewer.append(element)
    # We've found a raw file
    elif re.search("[http|https]://raw.github.com/.*$",element[1]):
    #    print "RAW: %s" %element[1]
        raw_files.append(element)
    # github io address associated with repo
    elif re.search("[http|https]://.*[.]github.io/.*$",element[1]):
        github_io.append(element)
    elif re.search("[http|https]://.*[.]github.com/.*$",element[1]):
        github_io.append(element)
    # github io address for entire association
    elif re.search("[http|https]://.*[.]github.io$",element[1]):
        github_io_master.append(element)
    elif re.search("[http|https]://.*[.]github.com$",element[1]):
        github_io_master.append(element)
    #    print "IO: %s" %element[1]
    else:
        rest.append(element)

# These are ready for parsing
urls = dict()
urls["raw_files"] = raw_files
urls["gists"] = gists # will parse later
urls["repos"] = inputs
urls["github_io"] = github_io_master # we can't obtain specific repos
urls["github_help"] = github_help
urls["github_users"] = users
urls["nbviewer"] = nbviewer # will parse later

# For github_io urls, we need to convert to repo url
while len(github_io) > 0:
    element = github_io.pop()
    print "Parsing %s, %s more to go!" %(element[1],len(github_io))
    url = element[1].replace("http://","").replace("https://","")
    user_name =  url.split("/")[0].split(".")[0]
    repo_name = url.split("/")[1]
    new_url = "http://www.github.com/%s/%s" %(user_name,repo_name)
    response = requests.get(new_url)
    if response.status_code == 200:
        element = (element[0],new_url)
        urls["repos"].append(element)
    else:
        rest.append(element)


# Manual curation
len(rest)
# 134
urls["github_io"].append(('26110025', u'https://github.com/qsardb'))
urls["raw_files"].append(('22934238', u'http://imagejs.org/imagejs.js'))

false_hits = [('25071829', u'http://thenextweb.com/dd/2014/03/17/mozilla-science-lab-github-figshare-team-fix-citation-code-academia'),
              ('23448176', u'http://readwrite.com/2011/06/02/github-has-passed-sourceforge'),
              ('25940563', u'http://iphylo.blogspot.de/2013/04/time-to-put-taxonomy-into-github.html'),
              ('25995958', u'https://play.google.com/store/apps/details?id=com.github.browep.thinspo'),
              ('22291635', u'http://marciovm.com/i-want-a-github-of-science'),
              ('26836305', u'https://urldefense.proofpoint.com/v2/url?u=https-3A__github.com_dlaszlo88_eLIFE-2DNPM-5FNMRrelaxation&'),
              ('26981420', u'http://cole-trapnelllab.github.io/cufflinks/igenome_table/index.html'),
              ('26516857', u'http://msoon.github.io/powermonitor/PowerTool/doc/PowerMonitorManual.pdf'),
              ('24132163', u'http://cloud.github.com/downloads/hadley/ggplot2/guide-col.pdf'), 
              ('24132163', u'http://cloud.github.com/downloads/hadley/ggplots2/guide-col.pdf'),
              ('26236402', u'http://atrichlewis42.github.io/synergy-maps'),
              ('26812047', u'http://guinea-ebov.github.io/code/files/sitreps/hebdo/SitRep_hebdo_Guinee_Semaine13_2015.pdf')
]

urls["false_hits"] = false_hits

rest = [('25849488', u'https://github.com/najoshi/sickle'), 
        ('25984347', u'http://github.com/JackKelly/rfm_ecomanager_logger'),
        ('26560745', u'https://github.com/jyeatman/AFQ'),
        ('25559943', u'https://github.com/networkx/networkx'),
        ('25273974', u'http://github.com/gersteinlab/FunSeq2'), 
        ('26783965', u'http://www.github.com/stschiff/sequenceTools'),
        ('26783965', u'http://www.github.com/stschiff/rarecoal'),
        ('26783965', u'http://www.github.com/stschiff/msmc'), 
        ('22772437', u'https://www.github.com/tk2/RetroSeq'),
        ('23826173', u'https://github.com/michaelbarton/genomer'), 
        ('23826173', u'https://github.com/michaelbarton/chromosome-pfluorescens-r124-plasmid'), 
        ('23826173', u'https://github.com/michaelbarton/chromosome-pfluorescens-r124-genome'), 
        ('23812995', u'http://github.com/kortschak/biogo'), 
        ('25271284', u'https://github.com/picrust/picrust'),
        ('24324759', u'https://github.com/ekg/smithwaterman'),
        ('25977800', u'https://github.com/preprocessed-connectomes-project/quality-assessment-protocol'), 
        ('25730631', u'https://github.com/ekg/freebayes'), 
        ('26740918', u'https://github/jyeatman/AFQ'), 
        ('26271043', u'https://github.com/jstjohn/SeqPrep'), 
        ('26271043', u'https://github.com/ekg/vcflib'), 
        ('26575292', u'https://github.com/broadinstitute/picard'), 
        ('25385532', u'https://github.com/rneher/FitnessInference'), 
        ('25875171', u'https://githubcom/najoshi/sickle'), 
        ('24260458', u'https://github.com/picrust/picrust'),
        ('26628921', u'https://github.molgen.mpg.de/loosolab/admire'),
        ('26218351', u'https://github.com/McCRIBS/McCRIBS'),
        ('26089767', u'http://www.github.com/networkx/networkx'),
        ('25361575', u'https://github.com/molgenis/molgenis'),
        ('25932347', u'https://github.com/ntncmch/ebola_sierra_leone'),
        ('26973785', u'https://github.com/doxygen/doxygen'),
        ('26973785', u'https://github.com/doxygen/doxygen'),
        ('25549342', u'https://github.com/kinome/kinome.github.io'),
        ('26897027', u'https://github.com/charite/topodombar'),
        ('26400485', u'https://github.com/broadinstitute/picard'), 
        ('26242175', u'https://github.com/broadinstitute/picard'), 
        ('25306138', u'https://github.com/broadinstitute/picard'),
        ('26564201', u'https://github.com/broadinstitute/picard'),
        ('26496891', u'https://github.com/broadinstitute/picard'), 
        ('25473421', u'https://github.com/broadinstitute/picard'),
        ('25888430', u'https://github.com/broadinstitute/picard'), 
        ('26872740', u'https://github.com/broadinstitute/picard'),
        ('26444573', u'https://github.com/broadinstitute/picard'), 
        ('25759012', u'https://github.com/broadinstitute/picard'), 
        ('25859758', u'https://github.com/broadinstitute/picard'), 
        ('26687620', u'https://github.com/broadinstitute/picard'), 
        ('25505934', u'https://github.com/broadinstitute/picard'),  
        ('26315209', u'https://github.com/broadinstitute/picard'), 
        ('25164765', u'https://github.com/broadinstitute/picard'), 
        ('25903198', u'https://github.com/broadinstitute/picard'), 
        ('26527727', u'https://github.com/ENCODE-DCC/pyencoded-tools'),
        ('20106815', u'https://github.com/mz2/imotifs'),
        ('25339461', u'https://github.com/broadinstitute/picard'), 
        ('26543846', u'https://github.com/broadinstitute/picard'), 
        ('26125026', u'https://github.com/GMOD/jbrowse'), 
        ('25859288', u'https://github.com/broadinstitute/picard'), 
        ('25451469', u'https://github.com/aglatz/mineral-deposit-segmentation-pipeline'), 
        ('26771513', u'https://github.com/guinea-ebov/guinea-ebov.github.io'),
        ('26728183', u'https://github.com/broadinstitute/picard'), 
        ('26858705', u'https://github.com/broadinstitute/picard'),
        ('26510457', u'https://github.com/broadinstitute/picard'),
        ('26315624', u'https://github.com/broadinstitute/picard'), 
        ('26040329', u'http://www.github.com/networkx/networkx'),
        ('25903370', u'https://github.com/broadinstitute/picard'),
        ('26882539', u'https://github.com/dnanexus/dx-toolkit'),
        ('26296237', u'https://github.com/articlemetrics/articlemetrics.github.io'), 
        ('26296237', u'https://github.com/lagotto/pyalm'), 
        ('25371702', u'https://github.com/lorisfichera/lorisfichera.github.com'), 
        ('25157553', u'https://github.com/sensor2model-group/sensor2model'),
        ('26846686', u'https://github.com/EPICScotland/Broadwick'), 
        ('25408304', u'https://github.com/SlicerIGT/LumpNav'), 
        ('25892211', u'https://github.com/klusta-team/klustaviewa'), 
        ('24612771', u'https://github.com/faircloth-lab/edittag'), 
        ('26439627', u'https://github.com/dphenriksen/RegionDK'), 
        ('26675891', u'https://github.com/uomsystemsbiology/epidermal_data'), 
        ('23028546', u'https://github.com/FragIt/fragit-main'), 
        ('23020243', u'https://github.com/mikejiang/BioC2015OpenCyto'), 
        ('26671958', u'https://github.com/ntncmch/ebola_sierra_leone'), 
        ('26413745', u'https://github.com/plaque2/plaque2.github.io'), 
        ('26413745', u'https://github.com/plaque2/plaque2.github.io'), 
        ('26751378', u'https://github.com/neurokernel/neurokernel'), 
        ('26484246', u'https://github.com/broadinstitute/picard'), 
        ('26727204', u'https://github.com/broadinstitute/picard'), 
        ('26767617', u'https://github.com/broadinstitute/picard'), 
        ('26136847', u'https://github.com/broadinstitute/picard'), 
        ('26825632', u'https://github.com/broadinstitute/picard'), 
        ('25395669', u'https://github.com/broadinstitute/picard'), 
        ('26681494', u'https://github.com/broadinstitute/picard'), 
        ('26557050', u'https://broadinstitute.github.io/picard'), 
        ('26708082', u'https://github.com/broadinstitute/picard'),
        ('26061969', u'https://github.com/cytoscape/cytoscape.js'), 
        ('25489744', u'https://github.com/informaton/padaco'), 
        ('26114548', u'http://broadinstittute.github.io/picard'), 
        ('26798323', u'https://github.com/Trinotate/Trinotate'), 
        ('26753127', u'https://github.com/lh3/schemas'), 
        ('24758346', u'https://github.com/daob/JruleMplus'), 
        ('25653582', u'https://github.com/FCP-INDI/C-PAC'), 
        ('21124986', u'https://github.com/A1kmm/sbasetram'), 
        ('23741409', u'https://github.com/cjauvin/pypetree'), 
        ('26053998', u'https://github.com/FCP-INDI/C-PAC'), 
        ('25293757', u'https://github.com/codinghedgehog/phrecon'), 
        ('26692761', u'https://github.com/cole-trapnell-lab/cufflinks'), 
        ('26114585', u'http://broadinstittute.github.io/picard'), 
        ('26262622', u'https://github.com/scipy-lectures/scipy-lecture-notes'), 
        ('25887352', u'https://github.com/broadinstitute/picard'), 
        ('26642925', u'https://github.com/broadinstitute/picard'), 
        ('25239376', u'https://github.com/gemtools/gemtools-examples'), 
        ('25853327', u'https://github.com/broadinstitute/picard'), 
        ('26552596', u'https://github.com/broadinstitute/picard'),  
        ('26327537', u'https://github.com/broadinstitute/picard'), 
        ('26864517', u'https://github.com/broadinstitute/picard'), 
        ('26834993', u'https://github.com/broadinstitute/picard'), 
        ('26395405', u'https://github.com/broadinstitute/picard'), 
        ('26076356', u'https://github.com/broadinstitute/picard'), 
        ('26926343', u'https://github.com/broadinstitute/picard'), 
        ('26149272', u'https://github.com/broadinstitute/picard'), 
        ('25404257', u'https://github.com/broadinstitute/picard'), 
        ('26579211', u'https://github.com/broadinstitute/picard'), 
        ('26980001', u'https://github.com/broadinstitute/picard'), 
        ('25924671', u'https://github.com/broadinstitute/picard'), 
        ('26572163', u'https://github.com/broadinstitute/picard'),
        ('26289667', u'https://github.com/broadinstitute/picard'), 
        ('25884497', u'https://github.com/cole-trapnell-lab/cufflinks'), 
        ('20298518', u'https://github.com/asad/VFLib'), 
        ('25462216', u'https://github.com/demotu/BMC')]
 
urls["repos"] = urls["repos"] + rest
pickle.dump(urls,open("%s/inputs_categorized.pkl" %outfolder,"wb"))

jobfile = "%s/parse_repos.job" %(scripts)
filey = open(jobfile,'w')

seen = []
for repo in urls["repos"]:
    repo_url = repo[1]
    pubmed_paper = repo[0]
    if repo_url not in seen:
        print "Parsing %s" %(repo_url)
        seen.append(repo_url)
        repo_name = repo_url.split("/")[-1]
        user_name = repo_url.split("/")[-2]
        output_file = "%s/%s_%s_functions.tsv" %(outfolder,user_name,repo_name)
        if not os.path.exists(output_file):
            filey.writelines("python %s/parse_imports.py %s %s %s" %(scripts, repo_url, output_file, pubmed_paper))
           
filey.close()

len(seen)
# 4408

for label,url_list in urls.iteritems():
    print "count %s for %s" %(label,len(url_list))

# count repos for 5570
# count github_io for 183
# count nbviewer for 19
# count raw_files for 16
# count false_hits for 12
# count gists for 58
# count github_help for 8
# count github_users for 206
