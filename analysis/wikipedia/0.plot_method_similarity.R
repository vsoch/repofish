library(pheatmap)

sim = read.csv("../models/method_vectors_similarity.tsv",sep="\t",head=TRUE,stringsAsFactors=FALSE,row.names=1)

# Just plot as is
pdf("../models/method_vectors_similarity.pdf",width=12,height=12)
pheatmap(sim,cluster_rows=FALSE,cluster_cols=FALSE,title="Wikipedia Method Similarity")
pheatmap(title="Wikipedia Method Similarity")
dev.off()
