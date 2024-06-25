# Sonnet or Not, Bot?

This repository contains code and data for the following paper.

**Sonnet or Not, Bot? Poetry Evaluation for Large Models and Datasets**

<br><br>

## Data

The data in this repository includes:
- [1.4k+ public domain poems](data/poetry-evaluation_public-domain-poems.csv) tagged by poetic form by the Poetry Foundation, the Academy of American Poets, or both — with accompanying metadata such as subject tags and author birth and death dates where available
- retrieval metadata from [Dolma](https://allenai.github.io/dolma/) using the [WIMBD](https://github.com/allenai/wimbd) platform including source domains for each detected poem
- memorization predictions using n-gram overlap between true poems and generated poem continuations by GPT-4 

<br><br>

## Code

The code in this repository includes:
- a Python notebook demonstrating how to query for data from [Dolma](https://allenai.github.io/dolma/) using the [WIMBD](https://github.com/allenai/wimbd) platform
- a Python notebook analyzing the query data from Dolma
- a Python notbeook demonstrating the memorization experiments
- Python scripts demonstrating how to prompt models for the poetry form classifcation task
- a Python notebook demonstrating analysis of classification results
