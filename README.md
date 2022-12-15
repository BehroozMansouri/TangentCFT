# TangentCFT
Tangent Combined FastText (Tangent-CFT) is a embedding model for mathematical formulas. When searching for mathematical content, accurate measures of formula similarity can help with tasks such as document ranking, query recommendation, and result set clustering. While there have been many attempts at embedding words and graphs, formula embedding is in its early stages. 
We introduce a new formula embedding model that we use with two hierarchical representations, (1) Symbol Layout Trees (SLTs) for appearance, and (2) Operator Trees (OPTs) for mathematical content. Following the approach of graph embeddings such as DeepWalk, we generate tuples representing paths between pairs of symbols depth-first, embed tuples using the fastText n-gram embedding model, and then represent an SLT or OPT by its average tuple embedding vector. We then combine SLT and OPT embeddings, leading to state-of-the-art results for the formula retrieval task of NTCIR-12.

# Requirements
The codebase is implemented in Python 3.6. Package versions used for development are in [requirement.txt](https://github.com/BehroozMansouri/TangentCFT/blob/master/requirements.txt) file.

# Dataset
To evaluate our embedding model we used [NTCIR-12 dataset](https://www.cs.rit.edu/~rlaz/NTCIR-12_MathIR_Wikipedia_Corpus.zip), focusing on formula retrieval task. The collection contains over 590000 mathematical formulas from Wikipedia with 20 formula queries with their relevant formulas. For comparison with previous approaches we used bpref score to evaluate the top-1000 relevant formulas. 
Also, one can easily use anydataset, such as [Math Stach Exchange] (https://math.stackexchange.com/), in form of csv file of latex formula and formula ids (separated by $$ sign) to train a new model. 

# Running TangentCFT
Here are the steps to do the Tangent-CFT embeddings. 
The first step to run TangentCFT is to set the configuration file which are the parameters for fastText. Also, one can specify the directory to save the output vector for each of the formulas for further analysis. The configuration file should be in Configuration directory, under the config directory with file name in format of config_x where x show the run id. Here is an example of configuration file:
```
context_window_size,20
hs,1
id,1
iter,1
max,6
min,3
negative,30
ngram,1
result_vector_file_path,None
skip_gram,1
vector_size,300

```
The next step is to decide to train a new model or load a previously trained model that is saved in Saved_model directory. To train a new model, one can simply set directory of NTCIR-12 (or other dataset) and configuration file id. Here is an example of running the model that runs the model with configurations 100 and 101 and saves the vector representations in the direcotry specified in the configuration file:
```
python3 tangent_cft_front_end.py -cid 1 -ds 'NTCIR-12_MathIR_Wikipedia_Corpus/MathTagArticles' --slt True -em 'encoder.csv'
```
The command above, use the configuration file, with id 1, use the NTCIR 12 dataset to train the model based on slt representation and saves the encoding map in encoder.csv file. To save the model one can use the command:
```
python3 tangent_cft_front_end.py -cid 2 -ds 'NTCIR-12_MathIR_Wikipedia_Corpus/MathTagArticles' --slt False -em 'encoder.csv' --mp 'opt_model' 
```
With this command, a model is trained based on OPT representation of NTCIR-12 dataset and result is saved in opt_model. Finally, to load a model, one can use the following command:
```
python3 tangent_cft_front_end.py -cid 2 -ds 'NTCIR-12_MathIR_Wikipedia_Corpus/MathTagArticles' --slt False -em 'encoder.csv' --mp 'opt_model' --t False --rf res_1
```
With this command, train model is set to false and model is loaded and retrieval result is saved in res_1 file in Retrieval_Results directory.

* **Checking the retrieval results.** After the model is trained and the retrieval is done, the results are saved the directory "Retrieval_Results". In each line of the result file, there is the query id followed by relevant formula id, its rank, the similarity score and run id. TangentCFT results on NTCIR-12 dataset is Retrieval_Results directory as the sample. To evaluate the results, the judge file of NTCIR-12 task, is located in the Evaluation directory with [Trec_eval tool](https://trec.nist.gov/trec_eval/). 

# References
Please cite Tangent-CFT: An Embedding Model for Mathematical Formulas paper. (Mansouri, B., Rohatgi, S., Oard, D. W., Wu, J., Giles, C. L., & Zanibbi, R. (2019, September). Tangent-CFT: An Embedding Model for Mathematical Formulas. In Proceedings of the 2019 ACM SIGIR International Conference on Theory of Information Retrieval (pp. 11-18). ACM.)
