# Sonnet or Not, Bot?

This repository contains code and data for the following paper.

**Sonnet or Not, Bot? Poetry Evaluation for Large Models and Datasets**

<br><br>

## Data

The data in this repository includes:
- [1.4k+ public domain poems](data/poetry-evaluation_public-domain-poems.csv) tagged by poetic form by the Poetry Foundation, the Academy of American Poets, or both — with accompanying metadata such as subject tags and author birth and death dates where available
- retrieval metadata from [Dolma]() using the [WIMBD]() platform including source domains for each detected poem

<br><br>

## Code

The code in this repository includes:
- a Python notebook demonstrating how to query for data from [Dolma]() using the [WIMBD]() platform
- Python scripts demonstrating how to prompt models for the poetry form classifciation task
- a Python notebook demonstrating analysis of classification results
