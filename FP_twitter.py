#!/usr/bin/env python
# coding: utf-8

# # Strenth of Friendship Paradox - Twitter Script
# This notebook processes Twitter @mention networks from Park et al. (2018). 

# In[1]:


# import libraries
import pandas as pd
import numpy as np
from itertools import chain
from collections import Counter
from math import log10
import os



def FP(df):
    '''calculate the strength of FP index'''
    fp = 1 + df['std']/df['mean']**2
    return(fp)

def summary_stat(df, percent = .5):
    '''
    calculate summary degree stat
    input: percent e.g., .5, .6, 1
    '''
    df['w'] = (df['f12'] +  df['f21'])/2
    df['d']  = abs(df['f12'] - df['f21'])
    cutoff = df['w'].quantile(percent)
    # calculate Mean and SD
    def sum_stat(degree_df):
        sum_df = degree_df.agg({'degree':['mean','std','min','max']})
        sum_df = sum_df.T.reset_index(drop=True)
        return(sum_df)
    # separate cases
    if percent == 1:
        # degree calculation
        A_degree = pd.DataFrame(list(Counter(df.loc[:,'node1'].append(df.loc[:,'node2'])).items()))
        A_degree.columns = ["node", "degree"]
        sum_df = sum_stat(A_degree)
        sum_df['type'] = 'All'
    else:
        # separate Strong vs. Weak
        S_df = df.loc[df.w >= cutoff,:]
        W_df = df.loc[df.w < cutoff,:]
        # degree calculaion
        S_degree = pd.DataFrame(list(Counter(S_df.loc[:,'node1'].append(S_df.loc[:,'node2'])).items()))
        S_degree.columns = ["node", "degree"]
        W_degree = pd.DataFrame(list(Counter(W_df.loc[:,'node1'].append(W_df.loc[:,'node2'])).items()))
        W_degree.columns = ["node", "degree"]
        sum_S = sum_stat(S_degree)
        sum_S['type'] = 'Strong'
        sum_W = sum_stat(W_degree)
        sum_W['type'] = 'Weak'
        sum_df = sum_S.append(sum_W)
    # add extra info
    sum_df['percentile'] = percent
    sum_df['cutoff'] = cutoff
    return(sum_df)



# create a list of bz2 files
bz2_list = [x for x in os.listdir('../data/') if x.endswith(".bz2")]
print(bz2_list)

# parse data to calculate FP
def country_stat(num_country):
    # read data
    d_name = bz2_list[num_country]
    df = pd.read_csv('../data/'+d_name, compression="bz2", sep="\t")
    # calculate basic stat
    stat_df = pd.concat([summary_stat(df, percent = x) for x in [.5,.6,.7,.8,.9,1]])
    # calculate FP
    stat_df['FP'] = FP(stat_df)
    stat_df['country'] = d_name.split(sep='_')[0]
    return(stat_df)



# create a summary stat table includes all the data
stat_df = pd.concat([country_stat(num_country = x) for x in range(len(bz2_list))])
# save it as a csv table
stat_df.to_csv('summary_twitter.csv', sep ='\t')

