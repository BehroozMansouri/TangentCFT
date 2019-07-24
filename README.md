# TangentCFT
Tangent Combined FastText (Tangent-CFT) is a embedding model for mathematical formulas. When searching for mathematical content, accurate measures of formula similarity can help with tasks such as document ranking, query recommendation, and result set clustering. While there have been many attempts at embedding words and graphs, formula embedding is in its early stages. 
We introduce a new formula embedding model that we use with two hierarchical representations, (1) Symbol Layout Trees (SLTs) for appearance, and (2) Operator Trees (OPTs) for mathematical content. Following the approach of graph embeddings such as DeepWalk, we generate tuples representing paths between pairs of symbols depth-first, embed tuples using the fastText n-gram embedding model, and then represent an SLT or OPT by its average tuple embedding vector. We then combine SLT and OPT embeddings, leading to state-of-the-art results for the formula retrieval task of NTCIR-12.

# Requirements
The codebase is implemented in Python 3.6. Package versions used for development are in [requirement.txt](https://github.com/BehroozMansouri/TangentCFT/blob/master/requirements.txt) file.

# Dataset
To evaluate our embedding model we used [NTCIR-12 dataset](https://www.cs.rit.edu/~rlaz/NTCIR-12_MathIR_Wikipedia_Corpus.zip), focusing on formula retrieval task. The collection contains over 590000 mathematical formulas from Wikipedia with 20 formula queries with their relevant formulas. For comparison with previous approaches we used bpref score to evaluate the top-1000 relevant formulas. 

# Running TangentCFT
Here are the steps to do the Tangent-CFT embeddings. It is assumed that, tuples for each formula are extracted beforehand using Tangent-S (see [paper](https://dl.acm.org/citation.cfm?id=3080748) and [code](https://www.cs.rit.edu/~dprl/files/release_tangent_S.zip) ) in a separate file, with each tuple located in a line. With that assumption, the following steps are needed before training the model:

* **Generating the encoded values.** Using formula or tuple level encoder(located in Embedding Pre-processing directory), specify the directory where the formula tuples are at (-sd) and where to save the encoded values (-dd). Parameter --frp take value True or False, with value True ignoring the full relative path. Finally, --tokenization decided how the tuples should be encoded. It should be an integer between 1 to 4, with value 3 as the default. Given a tuple in form of (V!v, N!12, a), tokenization in each of the four modes will create the following characters:
 1. v,12,a
 2. V!,N!,a
 3. V!,v,N!,12,a
 4. V!v,N!12,a

Here is an example to run tuple-level encoder:

```
 python3 encoder_tuple_level.py -sd tuple_directory -dd encoded_tuple_directory --tokenization 2
```

* **Setting configuration of model.** The next step is to set the configuration of the model. The parameters for fastText and the file path to read the encoded tuples should be specified before training. Also, one can specify the directory to save the output vector for each of the formulas for further analysis. The configuration file should be in Configuration directory, under the config directory with file name in format of config_x where x show the run id. Here is an example of configuration file:
```
context_window_size,5
file_path_fasttext,/home/opt_tuple_directory/
hs,0
id,100
iter,10
max,6
min,3
negative,20
ngram,1
result_vector_file_path,/home/opt_encoded_values/
skip_gram,1
vector_size,300
```
* **Running Tangent-CFT.** At this stage, formulas and queries are encoded and saved in a directory. Configuration of the model is defined by the user. It is time to run Tangent-CFT to get embedding for formulas, queries and do the NTCIR-12 formula retrieval task. To run the model, one should specify all id of configuration file(s) which should be all located in the directory (Configuration/config). If users are intersted to save the vector representations of formulas for further analysis, they should set the *'sv'* parameter to True. Here is an example of running the model that runs the model with configurations 100 and 101 and saves the vector representations in the direcotry specified in the configuration file:
```
python3 runModule.py -cid 100 101 --sv True
```
* **Checking the retrieval results.** After the model is trained and the retrieval is done, the results are saved the directory "Retrieval_Results" in format of res_id where id is the configuration id. In each line of the result file, there is the query id followed by relevant formula id, its rank, the similarity score and run id. TangentCFT results on NTCIR-12 dataset is Retrieval_Results directory as the sample. To evaluate the results, the judge file of NTCIR-12 task, is located in the Evaluation directory with [Trec_eval tool](https://trec.nist.gov/trec_eval/). 

* **Combineing different models**

# References
Please cite Tangent-CFT: An Embedding Model for Mathematical Formulas paper.
