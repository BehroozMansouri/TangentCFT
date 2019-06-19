# TangentCFT
Tangent Combined FastText (Tangent-CFT) is a embedding model for mathematical formulas. 
This model is based on ealier works on graph embeddings where a graph was linearized and then a sequence embedding model was applied.

As mathematical formuals are rare and unique, one property we should be aware of is that our embedding model should be able to handle the unseen formuals (formulas not seen in the collection). Therefore, after linearizing the formulas we apply n-gram embedding model, which can handle unseen words better.Formulas in digital documents can be represented by their semantic or appearance, in this work, we use both representations.

Here are the steps to do the Tangent-CFT embeddings. It is assumed that, tuples for each formula is in a separate file, with each tuple located in a line.

</bold> Step 1: Generating the encoded values.
  Using formula or tuple level encoder(located in Embedding Preprocessing directory), specify the directory where the formula tuples are at (-sd parameter) 
