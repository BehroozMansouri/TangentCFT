# TangentCFT
Tangent Combined FastText (Tangent-CFT) is a embedding model for mathematical formulas. When searching for mathematical content, accurate measures of formula similarity can help with tasks such as document ranking, query recommendation, and result set clustering. While there have been many attempts at embedding words and graphs, formula embedding is in its early stages. 
We introduce a new formula embedding model that we use with two hierarchical representations, (1) Symbol Layout Trees (SLTs) for appearance, and (2) Operator Trees (OPTs) for mathematical content. Following the approach of graph embeddings such as DeepWalk, we generate tuples representing paths between pairs of symbols depth-first, embed tuples using the fastText n-gram embedding model, and then represent an SLT or OPT by its average tuple embedding vector. We then combine SLT and OPT embeddings, leading to state-of-the-art results for the formula retrieval task of NTCIR-12.

# Requirements
The codebase is implemented in Python 3.6. Package versions used for development are in [requirement.txt](https://github.com/BehroozMansouri/TangentCFT/blob/master/requirements.txt) file.

# Dataset
To evaluate our embedding model we used [NTCIR-12 dataset](https://www.cs.rit.edu/~rlaz/NTCIR-12_MathIR_Wikipedia_Corpus.zip), focusing on formula retrieval task. The collection contains over 590000 mathematical formulas from Wikipedia with 20 formula queries with their relevant formulas. For comparison with previous approaches we used bpref score to evaluate the top-1000 relevant formulas. 
Also one can easily use anydataset, such as [Math Stach Exchange] (https://math.stackexchange.com/), in form of csv file of latex formula and formula ids (separated by $$ sign) to train a new model. 

# Running TangentCFT
Here are the steps to do the Tangent-CFT embeddings. 
The first step to run TangentCFT is to set the configuration file which are the parameters for fastText. Also, one can specify the directory to save the output vector for each of the formulas for further analysis. The configuration file should be in Configuration directory, under the config directory with file name in format of config_x where x show the run id. Here is an example of configuration file:
```
context_window_size,20
hs,0
id,1
iter,30
max,6
min,3
negative,20
ngram,1
result_vector_file_path,None
skip_gram,1
vector_size,300

```
The next step is to decide to train a cft model. Here is a command to train and do retrieval with SLT representation:
```
python3 tangent_cft_front_end.py -ds "/NTCIR12_MathIR_WikiCorpus_v2.1.0/MathTagArticles" -cid 1  -em slt_encoder.tsv --mp slt_model --rf slt_ret.tsv --qd "/TestQueries" --ri 1
```
The command above, uses the configuration file, with id 1, use the NTCIR 12 dataset to train the model based on slt representation and saves the encoding map in slt_encoder.csv file and the cft model in file slt_model. The retrieval result with SLT representation is saved in file slt_ret.tsv 
Next, use the following command to do the same for OPT representation:
```
python3 tangent_cft_front_end.py -ds "/NTCIR12_MathIR_WikiCorpus_v2.1.0/MathTagArticles" --slt False -cid 2  -em opt_encoder.tsv --mp opt_model --tn False --rf opt_ret.tsv --qd "/TestQueries" --tn False --ri 2
```
Finally, to train the cft model on SLT Type representation and do the retrieval use the following command:
```
python3 tangent_cft_front_end.py -ds "/home/bm3302/Downloads/NTCIR12_MathIR_WikiCorpus_v2.1.0/MathTagArticles" -cid 3  -em slt_type_encoder.tsv --mp slt_type_model --rf slt_type_ret.tsv --qd "/TestQueries" --et 2 --tn False --ri 3  
```

The following three commands are used to train model on each representation and do retrieval. However, Tangent-CFT model, combines the three vector representations. Therefore, after training, use the following command to combine the retrieval results:
```
python3 tangent_cft_combine_results.py
```
The retrieval result will be saved in file cft_res.

**Checking the retrieval results.** After the model is trained and the retrieval is done, the results are saved the directory "Retrieval_Results". In each line of the result file, there is the query id followed by relevant formula id, its rank, the similarity score and run id. TangentCFT results on NTCIR-12 dataset is Retrieval_Results directory as the sample. To evaluate the results, the judge file of NTCIR-12 task, is located in the Evaluation directory with [Trec_eval tool](https://trec.nist.gov/trec_eval/). This file is **different** from the original NTCIR-12 judge file. There are some formula ids with special characters that in our model we have changed (normlized) their name, therefore, we normalized their name in judge file as well.

**Reproducability error.**
# References
Please cite Tangent-CFT: An Embedding Model for Mathematical Formulas paper. (Mansouri, B., Rohatgi, S., Oard, D. W., Wu, J., Giles, C. L., & Zanibbi, R. (2019, September). Tangent-CFT: An Embedding Model for Mathematical Formulas. In Proceedings of the 2019 ACM SIGIR International Conference on Theory of Information Retrieval (pp. 11-18). ACM.)
