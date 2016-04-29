library(pheatmap)

sim = read.csv("../models/method_vectors_similarity.tsv",sep="\t",head=TRUE,stringsAsFactors=FALSE,row.names=1)
sim[is.na(sim)] = 0
sim[is.null(sim)] = 0

# Just plot as is
pdf("../models/method_vectors_similarity.pdf",width=50,height=50)
pheatmap(sim,title="Wikipedia Method Similarity")
dev.off()
