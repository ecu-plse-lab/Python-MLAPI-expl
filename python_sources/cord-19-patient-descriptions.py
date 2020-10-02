#!/usr/bin/env python
# coding: utf-8

# CORD-19 Patient Descriptions
# ======
# 
# This notebook shows the query results for a single task. CSV summary tables can be found in the output section.
# 
# The report data is linked from the [CORD-19 Analysis with Sentence Embeddings Notebook](https://www.kaggle.com/davidmezzetti/cord-19-analysis-with-sentence-embeddings).

# In[ ]:


from cord19reports import install

# Install report dependencies
install()


# In[ ]:


get_ipython().run_cell_magic('capture', '--no-display', 'from cord19reports import run\n\ntask = """\nid: 3\nname: patient_descriptions\n\n# Field definitions\nfields:\n    common: &common\n        - name: Date\n        - name: Study\n        - name: Study Link\n        - name: Journal\n        - name: Study Type\n\n    asymptomatic: &asymptomatic\n        - {name: Age, query: median patient age, question: What is median patient age}\n        - {name: Sample Obtained, query: throat respiratory fecal sample, question: What sample}\n        - {name: Asymptomatic Transmission, query: proportion percent asymptomatic patients, question: What percent asymptomatic}\n        - {name: Excerpt, query: proportion percent asymptomatic patients, question: What percent asymptomatic, snippet: true}\n\n    incubation: &incubation\n        - {name: Age, query: median patient age, question: What is median patient age}\n        - {name: Days, query: range of incubation period days, question: What is median incubation period}\n        - {name: Range (Days), query: range of incubation periods days, question: What is incubation period range}\n\n    appendix: &appendix\n        - name: Sample Size\n        - name: Sample Text\n        - name: Study Population\n        - name: Matches\n        - name: Entry\n\nCan the virus be transmitted asymptomatically or during the incubation period_:\n    query: Asymptomatic transmission\n    columns:\n        - *common\n        - *asymptomatic\n        - *appendix\n\nHow does viral load relate to disease presentations and likelihood of a positive diagnostic test_:\n    query: viral load relation to positive diagnostic test\n    columns:\n        - *common\n        - {name: Age, query: median patient age, question: What is median patient age}\n        - {name: Sample Obtained, query: throat respiratory fecal sample, question: What sample}\n        - {name: Excerpt, query: $QUERY, question: What is $QUERY, snippet: True}\n        - *appendix\n\nIncubation period across different age groups:\n    query: Incubation period children adult elderly days\n    columns:\n        - *common\n        - *incubation\n        - *appendix\n\nLength of viral shedding after illness onset:\n    query: Shedding duration days\n    columns:\n        - *common\n        - *incubation\n        - *appendix\n\nManifestations of COVID-19 including but not limited to possible cardiomyopathy and cardiac arrest:\n    query: virus related manifestations\n    columns:\n        - *common\n        - {name: Age, query: median patient age, question: What is median patient age}\n        - {name: Sample Obtained, query: throat respiratory fecal sample, question: What sample}\n        - {name: Manifestation, query: clinical manifestations, question: What manifestations}\n        - {name: Frequency of Symptoms, query: symptoms frequency, question: What was frequency of symptoms}\n        - {name: Excerpt, query: clinical manifestations, question: What manifestations, snippet: True}\n        - *appendix\n\nProportion of all positive COVID19 patients who were asymptomatic:\n    query: Proportion of asymptomatic patients\n    columns:\n        - *common\n        - *asymptomatic\n        - *appendix\n\nProportion of pediatric COVID19 patients who were asymptomatic:\n    query: Asymptomatic pediatric patients\n    columns:\n        - *common\n        - *asymptomatic\n        - *appendix\n\nWhat is the incubation period of the virus_:\n    query: Range of incubation periods days\n    columns:\n        - *common\n        - *incubation\n        - *appendix\n"""\n\n# Build and display the report\nrun(task)')
