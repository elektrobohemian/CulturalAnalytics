# See all the "as ..." contructs? They're just aliasing the package names.
# That way we can call methods like plt.plot() instead of matplotlib.pyplot.plot().
import numpy as np
import scipy as sp
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import pandas as pd
import time
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 100)
pd.set_option('display.notebook_repr_html', True)
import seaborn as sns
sns.set_style("whitegrid")
sns.set_context("poster")

from bs4 import BeautifulSoup
from collections import OrderedDict # provides the ordered dictionary
import re # for regular expressions used below
import urllib # to read from URLs
import json
import networkx as nx # network analysis
from networkx.readwrite import json_graph
import itertools
import os.path
from datetime import datetime # for time measurement
import sys
import os
import pickle
import subprocess as subp
import gzip
import math

from jellyfish import jaro_distance, jaro_winkler, hamming_distance, levenshtein_distance
import scipy.cluster.hierarchy as scipycluster

from skimage import io, exposure
from scipy.spatial import distance
# import the k-means algorithm
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics import pairwise_distances_argmin,pairwise_distances_argmin_min, pairwise_distances
from sklearn.metrics.pairwise import euclidean_distances

# OAI
from sickle import Sickle

import googlemaps

def printLog(text):
    now=str(datetime.now())
    print "["+now+"]\t"+text
    # forces to output the result of the print command immediately, see: http://stackoverflow.com/questions/230751/how-to-flush-output-of-python-print
    sys.stdout.flush()
    
def pickleCompress(fileName,pickledObject):
    printLog("Pickling to '%s'" %fileName)
    f = gzip.open(fileName,'wb')
    pickle.dump(pickledObject,f)
    f.close()
    printLog("Pickling done.")
    
def pickleDecompress(fileName):
    #restore the object
    printLog("Depickling from '%s'" %fileName)
    f = gzip.open(fileName,'rb')
    pickledObject = pickle.load(f)
    f.close()
    printLog("Depickling done.")
    return pickledObject

if not os.path.exists("./graphs/"):
        os.makedirs("./graphs/")
if not os.path.exists("./graphs/generics/"):
        os.makedirs("./graphs/generics/")        
if not os.path.exists("./html/"):
        os.makedirs("./html/")

# if you have run this notebook from top to bottom, you don't have to reload the data
df4=pickleDecompress('clean_dataframe_with_century.picklez')
grpCentury=df4.groupby("century")
#df4.shape

def createGenericGraph(consideredDataFrame):
    # for testing purposes it is handy to limit the number of records
    #consideredDataFrame=consideredDataFrame[(consideredDataFrame.Year>=1961) & (consideredDataFrame.Year<1975)]

    # create an empty graph from the nx (networkx) package imported above
    G=nx.Graph()

    rowCount=0
    seenCreators=[]
    seenLocations=[]
    # [u'PPN', u'alternative', u'creator', u'dataProvider', u'date', 
    # u'description', u'format', u'identifier', u'isShownAt', u'issued', 
    # u'object', u'provider', u'publisher', u'relation', u'rights', u'source', 
    # u'spatial', u'subject', u'title', u'type', u'spatialClean', u'dateClean', 
    # u'spatialCluster', u'spatialClusterName', u'latitude', u'longitude', u'century']
    ignoreList=[u'rights', u'issued',u'source',u'spatial',u'dataProvider', u'date',u'format',u'spatialCluster',u'century', u'provider']
    for row in consideredDataFrame.iterrows():#itertuples(): 
    	rowCount=rowCount+1
    	if rowCount % 1000==0:
    		printLog("Processed %i rows..." % rowCount)
        ppn=val=row[1]["PPN"]
        G.add_node(ppn)
        G.node[ppn]['name'] = ppn
        G.node[ppn]['type'] = "PPN"
            
        keys=row[1].keys()
        for k in keys:
            elementEmpty=False
            if k not in ignoreList:
                #print k
                val=row[1][k]
                if val: 
                    if type(val) is float:
                        if not math.isnan(val):
                            #print row[1][k]
                            pass
                        else:
                            #print "I DON'T KNOW!"
                            elementEmpty=True
                    else:
                        #print row[1][k]
                        pass
                else:
                    #print "I DON'T KNOW!"
                    elementEmpty=True
                
                # only process non-empty elements
                if not elementEmpty:
                    if not val in G.nodes():
                        G.add_node(val)
                        G.node[val]['name'] = val
                        G.node[val]['type'] = k
                    
                    G.add_edge(ppn,val)
       

    return G

printLog("Creating graphs incl. PPNs...")

graphsPerCentury=dict()
for century in range(17,18):#(7,21): # we know that there are only media from the 7th century on
    if century in grpCentury.groups:
        centDF=grpCentury.get_group(century)
        returnedGraph=createGenericGraph(centDF)
        graphsPerCentury[century]=returnedGraph
        gmlPath="graphs/generics/full_"+str(century)+".gml"
        # export as GraphML, which can be read by Gephi
        nx.write_gml(returnedGraph,gmlPath)
        printLog("Graph for century %i built with %i nodes and %i edges (see %s)."%(century, len(returnedGraph.nodes()),len(returnedGraph.edges()),gmlPath))
printLog("Done.")