from repofish.utils import save_json
import numpy
import pandas
import json

folder = "/home/vanessa/Documents/Dropbox/Code/Python/repofish/analysis/pypi"
packages = pandas.read_csv("%s/pypi_filtered.tsv" %folder,sep="\t",index_col=0)
meta_folder = "%s/packages" %(folder) 

# Making a dataframe will take too much memory, let's make nodes and links

# Let's try sigma js export

# {"nodes": [
#    {
#        "id": "chr1",
#        "x": 0,
#        "y": 0,
#        "label": "Bob",
#        "size": 8.75
#    },
#    {
#        "id": "chr10",
#        "label": "Alice",
#        "x": 3,
#        "y": 1,
#        "size": 14.75
#    }
#],
#"edges": [{
#    "id": "1",
#    "source": "chr1",
#    "target": "chr10"
#}]

# ONLY INCLUDE PACKAGES WITH DEPENDENCIES #########################################################

nodes = []
single_nodes = [] # nodes in graph without dependencies (that will need to be added)
node_lookup = dict()

# NODES #####################################################################
def make_node(package_name,meta,node_count):
    return {"name":package_name,
            "size":len(meta["requires_dist"]),
            "color":"#999",
            "id":node_count,
            "description":meta["description"],
            "downloads":meta["downloads"],
            "keywords":meta["keywords"],
            "license":meta["license"],
            "maintainer":meta["maintainer_email"],
            "author":meta["author_email"]}

count=0
for row in packages.iterrows():
    package_name = row[1].package
    meta_file = "%s/%s.json" %(meta_folder,package_name)
    if os.path.exists(meta_file):
        meta = json.load(open(meta_file,"r"))
        if "requires_dist" in meta["info"]:
            if package_name not in node_lookup:
                node = make_node(package_name,meta["info"],count)
                nodes.append(node)
                node_lookup[package_name] = count
                count+=1
            dependencies = meta["info"]["requires_dist"]
            dependencies = [x.split(" ")[0].strip() for x in dependencies]
            for dep in dependencies:
                if dep not in node_lookup:
                    single_nodes.append(dep)

# Generate nodes for single_nodes list
# Note: did not wind up doing this to not clutter visualization
#for package_name in single_nodes:
#    meta_file = "%s/%s.json" %(meta_folder,package_name)
#    if os.path.exists(meta_file):
#        meta = json.load(open(meta_file,"r"))
#        node = make_node(package_name,meta["info"],count)
#        nodes.append(node)
#        node_lookup[package_name] = count
#        count+=1


# LINKS ##############################################################################

links = []
seen_links = []

def make_link(source,target):
    return {"id":"%s_%s" %(source,target),"source":source,"target":target}

for row in packages.iterrows():
    package_name = row[1].package
    meta_file = "%s/%s.json" %(meta_folder,package_name)
    if os.path.exists(meta_file):
        meta = json.load(open(meta_file,"r"))
        if "requires_dist" in meta["info"] and package_name in node_lookup:
            dependencies = meta["info"]["requires_dist"]
            dependencies = [x.split(" ")[0].strip() for x in dependencies]
            package_id = node_lookup[package_name]
            for dep in dependencies:
                if dep in node_lookup:
                    dep_id = node_lookup[dep]
                    link_id = "%s_%s" %(dep_id,package_id)
                    if link_id not in seen_links:
                        link = make_link(dep_id,package_id)
                        links.append(link)
                        seen_links.append(link_id)


# Save to file
res = {"nodes":nodes,"links":links}
os.mkdir("web")
save_json(res,"web/pypi.json")

# REPOFISH FLASK ####################################################################
nodes = dict()

def do_encode(param):
    if param != None:
        return param.encode("utf-8")
    else:
        return ""

# Data preparation for repofish flask application
def make_node(package_name,meta,node_count):
    return {"name":do_encode(package_name),
            "id":node_count,
            "description":do_encode(meta["description"]),
            "downloads":[do_encode(x) for x in meta["downloads"]],
            "keywords":do_encode(meta["keywords"]),
            "license":do_encode(meta["license"]),
            "maintainer":do_encode(meta["maintainer_email"]),
            "author":do_encode(meta["author_email"]),
            "package_url":do_encode(meta["package_url"]), 
            "release_url":do_encode(meta["release_url"]),
            "docs":do_encode(meta["docs_url"]),
            "url":do_encode(meta["home_page"]),
            "summary":do_encode(meta["summary"]),
            "version":do_encode(meta["version"])}

count=0
for row in packages.iterrows():
    package_name = row[1].package
    meta_file = "%s/%s.json" %(meta_folder,package_name)
    if os.path.exists(meta_file):
        meta = json.load(open(meta_file,"r"),encoding="utf-8")
        if package_name not in nodes:
            node = make_node(package_name,meta["info"],count)
            nodes[package_name] = node
            count+=1

pickle.dump(nodes,open("web/packages.nodes.pkl","w"))

# We also need a links lookup, links to keep based on package
links = dict()

def make_link(source,target):
    return {"id":"%s_%s" %(source,target),"source":source,"target":target}

for row in packages.iterrows():
    package_name = row[1].package
    meta_file = "%s/%s.json" %(meta_folder,package_name)
    if os.path.exists(meta_file):
        meta = json.load(open(meta_file,"r"))
        if "requires_dist" in meta["info"] and package_name in node_lookup:
            dependencies = meta["info"]["requires_dist"]
            dependencies = [x.split(" ")[0].strip() for x in dependencies]
            package_id = nodes[package_name]["id"]
            link_list = []
            for dep in dependencies:
                if dep in nodes:
                    dep_id = nodes[dep]["id"]
                    link_id = "%s_%s" %(dep_id,package_id)
                    link = make_link(dep_id,package_id)
                    link_list.append(link)
            links[package_name] = link_list

pickle.dump(links,open("web/packages.links.pkl","w"))
