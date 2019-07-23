# TangentCFT
Tangent Combined FastText (Tangent-CFT) is a embedding model for mathematical formulas. When searching for mathematical content, accurate measures of formula similarity can help with tasks such as document ranking, query recommendation, and result set clustering. While there have been many attempts at embedding words and graphs, formula embedding is in its early stages. 
We introduce a new formula embedding model that we use with two hierarchical representations, (1) Symbol Layout Trees (SLTs) for appearance, and (2) Operator Trees (OPTs) for mathematical content. Following the approach of graph embeddings such as DeepWalk, we generate tuples representing paths between pairs of symbols depth-first, embed tuples using the fastText n-gram embedding model, and then represent an SLT or OPT by its average tuple embedding vector. We then combine SLT and OPT embeddings, leading to state-of-the-art results for the formula retrieval task of NTCIR-12.

# Getting Started
Here are the steps to do the Tangent-CFT embeddings. It is assumed that, tuples for each formula are extracted beforehand using Tangent-S (see [paper](https://dl.acm.org/citation.cfm?id=3080748)  and [code](https://www.cs.rit.edu/~dprl/files/release_tangent_S.zip) ) in a separate file, with each tuple located in a line. With that assumption, 

1. </bold> Step 1: Generating the encoded values.
  Using formula or tuple level encoder(located in Embedding Preprocessing directory), specify the directory where the formula tuples are at (-sd) and where to save the encoded values (-dd).  
</bold> Step 2: 
