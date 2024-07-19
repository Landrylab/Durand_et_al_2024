#!/usr/bin/env python
# coding: utf-8

# # Pipeline to retrieve DiMSum merge statistics

# Note: the first steps are ran on the server to generate the merge_stats.csv file.

# ## Import packages

# In[2]:


import glob
import pandas as pd
#import seaborn as sns
#import matplotlib.pyplot as plt
#get_ipython().run_line_magic('matplotlib', 'inline')


# ## Initialize variables

# In[3]:


# Paths on the server
dimsum_output_folder = '/home/rodur28/novaseq_run2_dimsum-latest/'

# # Script to run on server

# ## Get statistics

# In[195]:


list_df = []
for f in glob.glob(dimsum_output_folder+'/*/'):
    df = pd.DataFrame()
    experiment = f.split('/')[-2]
    for i, r in enumerate(glob.glob(f+'/tmp/3_align/*report')):
        sample_name = r.split('/')[-1].split('_')[0]
        split_nb = r.split('/')[-1].split('_')[-1].split('.')[0]
        with open(r, 'r') as report:
            linestats = report.readlines()[8:16]
        report.close()
        lstats = [l.split() for l in linestats]
        largs = [(' '.join(x[1:]), int(x[0])) for x in lstats]
        largs_dict = dict(largs)
        largs_dict['sample_name'] = sample_name
        largs_dict['split'] = split_nb
        entry = pd.DataFrame(largs_dict, index=[i])
        entry['experiment'] = experiment
        list_df.append(entry)

fulldf = pd.concat(list_df)
dfsort = fulldf.sort_values(by=['experiment', 'sample_name', 'split']).reset_index(drop=True)
dfsort


# ## Aggregate split chunks

# In[87]:


gby = fulldf.groupby(['experiment', 'sample_name']).agg('sum').reset_index()
gby


# ## Calculate ratios

# In[88]:


proportions = gby.loc[:, 'Pairs':].div(gby.Pairs, axis=0)
proportions.rename(columns=lambda x: 'Ratio '+x, inplace=True)
proportions


# ## Export dataframe

# In[89]:


dfexport = pd.concat([gby, proportions], axis=1)
dfexport


# In[ ]:


dfexport.to_csv(dimsum_output_folder+'/merge_stats.csv')