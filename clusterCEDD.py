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
import networkx as nx # network analysis
import itertools
import os.path
from datetime import datetime # for time measurement
import sys
import os
import pickle
import subprocess as subp
import gzip


from jellyfish import jaro_distance,levenshtein_distance
import scipy.cluster.hierarchy as scipycluster

from skimage import io, exposure
from scipy.spatial import distance
# import the k-means algorithm
from sklearn.cluster import KMeans, MiniBatchKMeans

# OAI
from sickle import Sickle

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

df4=pickleDecompress('clean_dataframe.picklez')
# overwrite every "nulled" column (i.e. NULL or NaN) with -1
df4[df4["dateClean"].isnull()]=-1

df4["century"]=df4["dateClean"].apply(lambda x: int(x)/100)

featureBaseDir="/Users/david/Documents/src/python/CulturalAnalytics/featureFiles/"
missingPPNs=[]
readPPNs=[]
featuresPPN=[]

printLog("Loading features...")
index=0
for row in df4.iterrows():
    index=index+1
    if index%10000==0:
        printLog("Processed %i documents."%index)
    ppn=str(row[1]["PPN"])
    if os.path.isfile(featureBaseDir+ppn+".csv"):
        #print ppn+" okay."
        featFile=open(featureBaseDir+ppn+".csv")
        for line in featFile:
            feature=line
        tokens=feature.split()
        harray=[]
        for t in tokens:
            harray.append(int(t,16))
        featFile.close()
        
        readPPNs.append(ppn)
        featuresPPN.append(np.array(harray,dtype=np.uint8))
    else:
        missingPPNs.append(ppn)
printLog("Done.")
printLog("Number of missing PPNs: %i"%len(missingPPNs))

feats=featuresPPN

# define the number of clusters to be found
true_k=1000
printLog("Clustering of %i elements started with %i as cluster target size."%(len(feats),true_k))
# initialize the k-means algorithm
#km = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
km=MiniBatchKMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
# apply the algorithm on the data
km.fit(feats)
printLog("Clustering finished.")

saveDir="/Users/david/Documents/src/python/CulturalAnalytics/html2/"
imgDir="file:///Users/david/Documents/src/python/CulturalAnalytics/tmp/"
#imgDir="file:///Volumes/2TB_WD/sbb_images/tmp/"
htmlHead="<html><head></head><body bgcolor='#000000'>"
htmlTail="</body></html>"
clusters=dict()
for i,val in enumerate(km.labels_):
    if val not in clusters:
        clusters[val]=[]
    clusters[val].append(readPPNs[i])
#print clusters
for i in clusters:
    htmlOut=open(saveDir+str(i)+".html","w")
    htmlOut.write(htmlHead+"\n")
    for ppn in clusters[i]:
        htmlOut.write("<img width='170' src='"+imgDir+ppn+".jpg' />")
    htmlOut.write(htmlTail)
    htmlOut.close()
