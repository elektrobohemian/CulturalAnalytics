
# coding: utf-8

# # do not run all cells at once, they are computationally intensive

# In[294]:

# The %... is an iPython thing, and is not part of the Python language.
# In this case we're just telling the plotting library to draw things on
# the notebook, instead of on a separate window.
#get_ipython().magic(u'matplotlib inline')
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


from jellyfish import jaro_distance,levenshtein_distance
import scipy.cluster.hierarchy as scipycluster

# OAI
from sickle import Sickle

def printLog(text):
    now=str(datetime.now())
    print "["+now+"]\t"+text
    # forces to output the result of the print command immediately, see: http://stackoverflow.com/questions/230751/how-to-flush-output-of-python-print
    sys.stdout.flush()


# In[295]:

#get_ipython().system(u'pip install jellyfish')


# Stabi-URL:
# 
# PPN722144857
# 
# http://ngcs.staatsbibliothek-berlin.de/?action=metsImage&format=jpg&metsFile=PPN722144857&divID=PHYS_0001&width=800&rotate=0
# 
# http://ngcs.staatsbibliothek-berlin.de/?action=metsImage&format=jpg&metsFile=PPN730725200&divID=PHYS_0001&width=800&rotate=0

# In[296]:

# connect to a metadata repository
sickle = Sickle('http://digital.staatsbibliothek-berlin.de/oai')
# get the sets from the data provider connected to
sets = sickle.ListSets()
# print the returned sets including their identifiers
print "Sets provided by data provider\n* * * * * * * * * * * * * * * * * * * * * " # \n creates a new line
for s in sets:
    print "'"+s.setName+"' accessible via: '"+s.setSpec+"'"


# In[297]:

# get the records from this repository's specific document set 'DC_krieg.1914.1918' (documents related to World War I) 
# using Dublin Core format 
records = sickle.ListRecords(metadataPrefix='oai_dc', set='DC_all')


# In[298]:

# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#
# If you set 'allowDownloads' to True, the next steps will take a lot of time
#
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
allowDownloads=False

# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#
# If you set 'demoClustering' to False, the clustering steps will take about 2 hours
#
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
demoClustering=True


# In[299]:

savedRecords=[]
if allowDownloads:
    printLog("Starting OAI record download...")
    # initialize some variables for counting and saving the metadata records
    savedDocs=0
    # 2:15 h for 100k
    maxDocs=120000 # 100 is just for testing, for more interesting results increase this value to 1000. ATTENTION! this will also take more time for reading data.

    # save the records locally as we don't want to have to rely on a connection to the OAI-PMH server all the time
    # iterate over all records until maxDocs is reached
    # ATTENTION! if you re-run this cell, the contents of the savedRecords array will be altered!
    for record in records:
        # check if we reach the maximum document value
        if savedDocs<maxDocs:
            savedDocs=savedDocs+1
            # save the current record to the "savedRecords" array
            savedRecords.append(record.metadata)
            if savedDocs%1000==0:
                printLog("Downloaded %d of %d records."%(savedDocs,maxDocs))
        # if so, end the processing of the for-loop
        else:
            break # break ends the processing of the loop

    printLog("Finished OAI download of "+str(len(savedRecords))+" records.")
    pickle.dump( savedRecords, open( "save_120k_dc_all.pickle", "wb" ) )


# In[300]:

#pickledRecords=pickle.load( open( "save_100k_dc_all.pickle", "rb" ) )
availableKeys=dict()

evenRecords=[]
oddRecords=[]
for i,r in enumerate(savedRecords):
    for k in r.keys():
        if not k in availableKeys:
            availableKeys[k]=1
        else:
            availableKeys[k]=availableKeys[k]+1
    if i%2==0:
        evenRecords.append(r)
    else:
        oddRecords.append(r)

#pickle.dump( evenRecords, open( "even_dc_all.pickle", "wb" ) )
#pickle.dump( oddRecords, open( "odd_dc_all.pickle", "wb" ) )


# In[301]:

# immer als Array hinterlegt
# bei publisher entfernen: u"Staatsbibliothek zu Berlin \xe2\x80\x93 Preu\xc3\x9fischer Kulturbesitz, Germany"
# object: Bild zur Repräsentation
# type: Monographie o.ä.
# title
# spatial Ort
# subject Klassifikatoren wie Theologie
# identifier[1] = PPN


# even: Macbook
# odd: iMac



#savedRecords=pickle.load( open( "save_120k_dc_all.pickle", "rb" ) )
countSavedRecords=len(savedRecords)
printLog("Started image download and processing. This will take a while...")
#logFile = open("/Volumes/2TB_WD/sbb_images/downloadIssues.txt", "w")
logFile = open("./downloadIssues.txt", "w")

for i,record in enumerate(savedRecords):
    if i%1000==0:
        printLog("Downloading image %d of %d images."%(i,countSavedRecords))
    downloadDir="/Volumes/2TB_WD/sbb_images/tmp/"
    #downloadDir="./tmp/"
    ppn=""
    if len(record["identifier"])>1:
        ppn=str(record["identifier"][1])
    else:
        ppn=str(record["identifier"][0])
    ppnTIFF=ppn+".tif"
    ppnJPEGPAth=downloadDir+ppn+".jpg"
    if "object" in record.keys():
        # prevent downloading of already present files
        if not os.path.isfile(ppnJPEGPAth) :
            # check for the HTTP error code, maybe the file does not exist
            httpCode=urllib.urlopen(record["object"][0],downloadDir+ppnTIFF).getcode()
            if httpCode==200:
                if allowDownloads:
                    urlinfo=urllib.urlretrieve(record["object"][0],downloadDir+ppnTIFF)
                    ret=subp.call(["mogrify", "-resize","512x512","-format", "jpg",downloadDir+ppnTIFF])
                    if ret!=0:
                        print "Problem with mogrifying "+ppnTIFF
                        logFile.write("[MOGRIFY]: %s \n%s\n\n" % (str("Problem with mogrifying "+ppnTIFF),str("Downloaded from: "+record["object"][0])))
                    ret=subp.call(["rm",downloadDir+ppnTIFF])
                    if ret!=0:
                        print "Problem with removing "+ppnTIFF
                        logFile.write("[REMOVAL]: %s\n\n" % "Problem with removing "+ppnTIFF)
            else:
                print "Problem with accessing "+ppnTIFF+ " due to HTTP code: "+str(httpCode)
                logFile.write("[HTTP]: %s\n\n" % "Problem with accessing "+ppnTIFF)
                logFile.write("HTTP Code: "+str(httpCode)+"\n")
                logFile.write(str(urlinfo[1])+"\n\n")
    else:
        logFile.write("[OBJECT key missing]: %s\n\n" % str(record))
logFile.close()
print "\n"
printLog("Finished image download and processing.")


# 85.566 Bilder
# 
# ergibt Bilder "PPN813124174-0.jpg"/"PPN813124174-1.jpg", wobei eins von schlechter Qualitaet ist
# 
# wenn kein bilder gedownloadet werden konnten, dann handelt es sich in der regel um folgende types:
# 
# * Periodical
# * Multivolume work
# 
# an die METS-Daten kommt man über http://digital.staatsbibliothek-berlin.de/metsresolver/?PPN=PPN721220665

# In[302]:

# load the records
printLog("Loading pickled records...")
savedRecords=pickle.load( open( "save_120k_dc_all.pickle", "rb" ) )
printLog("Finished loading pickled records.")

availableKeys=dict()

for i,r in enumerate(savedRecords):
    for k in r.keys():
        if not k in availableKeys:
            availableKeys[k]=1
        else:
            availableKeys[k]=availableKeys[k]+1
    
print availableKeys

# create a dictionary for the records
values=dict()
# take the keys as they have found within the downloaded OAI records
keys=availableKeys.keys()
# for every metadata field, create an empty array as the content of the dictionary filed under the key 'k'
for k in keys:
    values[k]=[]
# in addition, store the PPN (the SBB's unique identifier for digitized content)    
values["PPN"]=[]

# iterate over all saved records
for record in savedRecords:
    # we cannot iterate over the keys of record.metadata directly because not all records cotain the same fields,...
    for k in keys:
        # thus we check if the metadata field 'k' has been created above
        if k in values:
            # append the metadata fields to the dictionary created above
            # if the metadata field 'k' is not available input "None" instead
            #values[k].append(record.get(k,["None"])[0].encode('ISO-8859-1'))
            if k in record:
                value=record.get(k)[0]
                if value.isdigit():
                    value=int(value)
                else:
                    value=value.encode('ISO-8859-1')
                values[k].append(value)
                # get the PPN
                if k=="identifier":
                    if len(record["identifier"])>1:
                        ppn=str(record.get(k)[1])
                    else:
                        ppn=str(record.get(k)[0])
                    values["PPN"].append(ppn)
            else:
                values[k].append(np.nan)
# create a data frame from the 
df=pd.DataFrame(pd.to_numeric(values,errors='coerce'))
df.shape


# In[303]:

df.head()


# In[304]:

df[df.PPN.isnull()].count()


# In[305]:

def uniqueValues(currentDataFrame):
    colNames=currentDataFrame.columns.values.tolist()
    for colName in colNames:
        print colName+";\t\t unique values:\t"+str(len(currentDataFrame[colName].unique()))+ "\t total count: "+str(currentDataFrame[colName].count())

uniqueValues(df)


# * https://www.maxmind.com/en/free-world-cities-database
# * http://www.geonames.org/export/
# * http://www.opengeocode.org/download.php#cities
# * https://en.wikipedia.org/wiki/Lists_of_cities_by_country

# In[306]:

# zum matchen: p.match
# regular expressions taken from: http://stackoverflow.com/questions/1449817/what-are-some-of-the-most-useful-regular-expressions-for-programmers
# extended by me

patterns=dict()

patterns["positiveInteger"]="^\d+$"
patterns["negativeInteger"]="^-\d+$"
patterns["generalInteger"]="^-?\d+$"
patterns["positiveFloat"]="^\d*\.\d+$"
patterns["negativeFloat"]="^-\d*\.\d+$"
patterns["generalFloat"]="^-?\d*\.\d+$"
patterns["positiveGermanFloat"]="^\d*,\d+$"
patterns["negativeGermanFloat"]="^-\d*,\d+$"
patterns["generalGermanFloat"]="^-?\d*,\d+$"
# Date (dd mm yyyy, d/m/yyyy, etc.), in range 1000-2099 without proper February handling
patterns["dateVariant"]="^([1-9]|0[1-9]|[12][0-9]|3[01])\D([1-9]|0[1-9]|1[012])\D(1[0-9][0-9][0-9]|20[0-9][0-9])$"
patterns["year"]="^(1[0-9][0-9][0-9]|20[0-9][0-9])$"
patterns["ancientYear"]="^([0-1]?[0-9][0-9][0-9]|20[0-9][0-9])$"
patterns["century"]="^(1[0-9][Xx][Xx]|20[Xx][Xx])$"
patterns["ancientCentury"]="^([0-1]?[0-9][Xx][Xx]|20[Xx][Xx])$"
patterns["decade"]="^(1[0-9][0-9][Xx]|20[0-9][Xx])$"
patterns["ancientDecade"]="^([0-1]?[0-9][0-9][Xx]|20[0-9][Xx])$"
# year range with splitter "- / :", the splitter can be surrounded by an arbitrary amount of whitespaces
patterns["rangeYear"]="^\s*(1[0-9][0-9][0-9]|20[0-9][0-9])\s*(\-|\/|:)\s*(1[0-9][0-9][0-9]|20[0-9][0-9])\s*$"
patterns["rangeCentury"]="^\s*(1[0-9][Xx][Xx]|20[Xx][Xx])\s*(\-|\/|:)\s*(1[0-9][Xx][Xx]|20[Xx][Xx])\s*$"
patterns["rangeAncientYear"]="^\s*([0-1]?[0-9][0-9][0-9]|20[0-9][0-9])\s*(\-|\/|:)\s*(1[0-9][0-9][0-9]|20[0-9][0-9])\s*$"
patterns["rangeAncientCentury"]="^\s*([0-1]?[0-9][Xx][Xx]|20[Xx][Xx])\s*(\-|\/|:)\s*(1[0-9][Xx][Xx]|20[Xx][Xx])\s*$"
patterns["rangeYear2Digit"]="^\s*(1[0-9][0-9][0-9]|20[0-9][0-9])\s*(\-|\/|:)\s*([0-9][0-9])\s*$"
patterns["rangeDateVariant"]="^\s*([1-9]|0[1-9]|[12][0-9]|3[01])\D([1-9]|0[1-9]|1[012])\D(1[0-9][0-9][0-9]|20[0-9][0-9])\s*(\-|\/|:)\s*([1-9]|0[1-9]|[12][0-9]|3[01])\D([1-9]|0[1-9]|1[012])\D(1[0-9][0-9][0-9]|20[0-9][0-9])\s*$"


patterns["email"]="^[_]*([a-z0-9]+(\.|_*)?)+@([a-z][a-z0-9-]+(\.|-*\.))+[a-z]{2,6}$"
patterns["domain"]="^([a-z][a-z0-9-]+(\.|-*\.))+[a-z]{2,6}$"
patterns["url"]="^https?\:\/\/[a-zA-Z0-9.-]+\.[a-zA-Z]{2,3}\/?$"
patterns["ipv4"]="^(?:\d{1,3}\.){3}\d{1,3}$"
patterns["rgbHex"]="^#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$"
patterns["generalHex"]="^#[a-fA-F0-9]*$"
 
patterns["isbnPrefix"]="^ISBN(-1(?:(0)|3))?:?\x20(\s)*[0-9]+[- ][0-9]+[- ][0-9]+[- ][0-9]*[- ]*[xX0-9]$"
patterns["isbn"]="^[0-9]+[- ][0-9]+[- ][0-9]+[- ][0-9]*[- ]*[xX0-9]$"
patterns["NaN"]="^[Nn][Aa][Nn]$"


# In[307]:

rowCount=0
histogram=dict()
for row in df.iterrows():
    rowCount=rowCount+1
    readDate=str(row[1]["date"])
    matchedOnce=False
    for key in patterns:
        p=re.compile(patterns[key])
        m = p.search(readDate)
        if m:
            if not key in histogram:
                histogram[key]=0
            histogram[key]=histogram[key]+1
            matchedOnce=True
        else:
            pass
    if not matchedOnce:
        print "No matches at all: "+row[1]["PPN"]+"\t for: "+str(readDate)
print "Row count: "+str(rowCount)
print histogram    


# In[308]:

class DataCleaner:
    # matches alphanumeric character and the underscore at the beginning of the string
    #Unicode flag is needed because of Asian character sets otherwise such signs would be considered as non-alphanumeric
    regEx_AlphaNum=re.compile("^\w",re.UNICODE)
    # checks for surrounding []; will match almost everything but Asian characters
    regEx_BracketText=re.compile("^\[[\w\?\.,\sßÄäÖöÜü]*\]",re.UNICODE)
    # checks for typical spellings of the "sine loco" abbreviation "s. l."
    regEx_SineLoco=re.compile("[sSoO]\s?\.\s?[lLoO]\s?\.?\s?",re.UNICODE)
    
    def __init__(self):
        pass
    
    def cleanAncientYearStrict(self,readData):
        if type(readData)==float:
            return readDate
        else:
            p=re.compile(patterns["ancientYear"])
            m = p.search(str(readData))
            if m:
                firstAppearance=m.group()
                return firstAppearance
            else:
                return np.nan
            
    def cleanSpatialText(self,readData):
        returnedString=""
        # just in case we did not get a string, we use brute force and return NaN
        if type(readData)==float:
            return ""
        else:
            #readData=str(readData)
            m = self.regEx_AlphaNum.search(readData)
            # if the string does start with a bracket...
            if not m:
                #print "No matches at all: "+row[1]["PPN"]+"\t for: "+str(readData)
                m2 = self.regEx_BracketText.search(readData)
                if m2:
                    matchedGroup=m2.group()
                    #print "\tMatch: "+matchedGroup
                    m3=self.regEx_SineLoco.search(matchedGroup)
                    if m3:
                        #print "\tMatched Sine Loco: "+str(m3.group())
                        return ""
                    else:
                        matchedGroup=matchedGroup.replace("[","").replace("]","")
                        #print "\tFinal string: "+matchedGroup
                        returnedString=matchedGroup
            # otherwise, it may still be a "sine loco"
            else:
                m3=self.regEx_SineLoco.search(readData)
                if m3:
                    #print "\tMatched Sine Loco: "+str(m3.group())
                    return ""
                else:
                    # in any case, there might be brackets left
                    returnedString=readData.replace("[","").replace("]","")
        
        # remove variants of "u.a."            
        regex = re.compile("[uU]\.\s?[aA]\.\s?",re.UNICODE)
        returnedString=regex.sub("",returnedString)
        return returnedString


# 1) wenn nicht alphanumerisch, dann alles zwischen dem ersten [] selektieren
# 2) prüfen, ob das != s.l. ist
# 3) ergebnis speichern
# * [s. l.] = sine loco (Latin: ohne Ortsangabe), Groß- und Kleinschreibung variiert, mit  oder; ebenso: o.O.
# * "[S.l.]  Cölln an der Spree" 
# * [Halle, Saale]  Hall
# * [Frankfurt, Oder]  [Frankfurt, Oder]
# * [Frankfurt, Oder?]
# * [Antwerpen?]
# * [Wittenberg]  Lipsiae  Lipsiae
# * [Stendal]  Leipzig
# * [Bando, Japan]
# * [Berlin-Lichterfelde]
# * [Köln]  Düsseldorf [u.a.]
# * [S.l.]  [Berlin?]
# * [Neuchâtel  Lausanne]
# * À Paris [usw.]
# * [London u.a.]
# * [China]

# In[309]:

dc=DataCleaner()

#for row in df.iterrows():
#    print dc.cleanSpatialText(str(row[1]["spatial"]))
    
df['spatialClean'] = df.spatial.apply(dc.cleanSpatialText)


# In[310]:

dc=DataCleaner()
df['dateClean'] = df.date.apply(dc.cleanAncientYearStrict)


# In[311]:

df.sort_values(by="date")


# # Ideen
# 
# * Timeline und Grafisches Aussehen, x-Achse: Zeit, y-Achse. Farbe? Brightness? Entropy? Abweichung vom Referenzbild (Distanz zum QBE)? https://www.slideshare.net/formalist/how-and-why-study-big-cultural-data-v2-15552598 #43
# * 

# see http://codereview.stackexchange.com/questions/37026/string-matching-and-clustering

# ### Example of The Things We Are Up To

# In[312]:

words = u'Berlin Balin Cölln Köln'.split()
print words

print "Number of words: %i" % len(words)
for i,val in enumerate(words):
    print str(i)+":\t "+str(val.encode('utf-8'))
    


# In[313]:

# http://docs.scipy.org/doc/numpy-1.10.1/reference/generated/numpy.triu_indices.html
# 2nd parameter:
# Diagonal above which to zero elements. k = 0 (the default) is the main diagonal, k < 0 is below it and k > 0 is above."""
# r= Return the indices for the upper-triangle of an (n, m) array. da m nicht angegeben ist, wird n=m angenommen
# m is not passed, hence m=n

# sagen, dass die matrix square ist!
r=np.triu_indices(n=len(words), k=1)
r


# what does this mean?
# $$
# A=
# \begin{pmatrix}
# a_{0,0} & \underline{a_{0,1}} & \underline{a_{0,2}} & \underline{a_{0,3}} \\
# \cdot & a_{1,1} & \underline{a_{1,2}} & \underline{a_{1,3}} \\
# \cdot & \cdot & a_{2,2} & \underline{a_{2,3}} \\
# \cdot & \cdot & \cdot & a_{3,3}
# \end{pmatrix}
# $$
# 

# In[314]:

def d_demo(coord):
    print coord
    i, j = coord
    # 1- wg. Distanz
    return 1 - jaro_distance(words[i], words[j])


# In[315]:

# http://docs.scipy.org/doc/numpy-1.10.1/reference/generated/numpy.set_printoptions.html
np.set_printoptions(precision=4)

# axis (3rd parameter): 0= along y axis, 1= along x axis
r2=np.apply_along_axis(d_demo, 0, r)
r2


# what does this mean for our matrix?
# $$
# A=
# \begin{pmatrix}
# a_{0,0} & \underline{0.1778} & \underline{0.4222} & \underline{0.3889} \\
# \cdot & a_{1,1} & \underline{0.4} & \underline{0.3667} \\
# \cdot & \cdot & a_{2,2} & \underline{0.2167} \\
# \cdot & \cdot & \cdot & a_{3,3}
# \end{pmatrix}
# $$
# 
# how to interpret: $a_{0,1}$, i.e., the difference between "Berlin" and "Balin" is 0.17777778.
# 
# why not the elements on the diagonal? because...

# In[316]:

print 1 - jaro_distance(words[1], words[1])


# ### the real stuff

# In[317]:

def d(coord):
    print "Altered d()"
    print coord
    i, j = coord
    return 1 - jaro_distance(unicode(str(words[i]), 'utf-8'), unicode(str(words[j]), 'utf-8'))


# In[318]:

df3=df.sort_values(by="date")#.head(100)
df3


# In[319]:

uniqueSpatials=df3["spatialClean"].unique()
words=None
if demoClustering:
    words=uniqueSpatials[:100] # only consider the first 10 elements for performance reasons
else:
    words=uniqueSpatials
r=np.triu_indices(len(words), 1)


# the next step would take approx. 1,75 hours on my MacBook Pro, hence we limited the number of spatial labels before

# In[320]:

printLog("Started calculations...")
# _ is the last evaluated value in an interactive shell
# axis (3rd parameter): 0= along y axis, 1= along x axis
r2=np.apply_along_axis(d, 0, r)
printLog("Finished calculations.")


# In[321]:

Z=scipycluster.linkage(r2)
if not demoClustering:
    pickle.dump( Z, open( "cluster_hierarchy_linkage_result_without_name_clustering.pickle", "wb" ) )


# In[322]:

clusters=scipycluster.fcluster(Z, t=0.1,criterion="distance")
# 2. parameter ist abhängig von der clustering strategie, -> cophenetic distance
# see: http://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.fcluster.html
# An array of length n. T[i] is the flat cluster number to which original observation i belongs.


# https://stat.ethz.ch/R-manual/R-devel/library/stats/html/cophenetic.html
# https://en.wikipedia.org/wiki/Cophenetic
clusters


# In[323]:

# 奈良 764
#if u"奈良".encode('utf-8') in uniqueSpatials:
#    print "supi!"


# In[324]:

#df3=df[df["spatialClean"].isin(words)]
#df["spatialClean"].isin(words)
#dfX=df[df["spatialClean"]=="奈良"]
#dfX["spatialClean"].isin(words)
#df3[df3["dateClean"]=="764"]


# In[325]:

def getWordIndex(word):
    return np.where(words==word)[0]

def getClusterID(data):
#for row in df3.iterrows():
    #data=row[1]["spatialClean"]
    #wordIndex=np.where(words==data)[0]
    #if data == u"奈良".encode('utf-8'):
    #    print "China!"
    #    wordIndex=getWordIndex(data)
    #    print wordIndex
    #    print clusters[wordIndex][0]
    wordIndex=getWordIndex(data)
    if wordIndex:
        return clusters[wordIndex][0]
    else:
        return ""


# In[326]:

#df3['spatialCluster'] = df3["spatialClean"].apply(getClusterID)


# i müsste Zeile sein
# 
# A 4 by (n-1) matrix Z is returned. At the i-th iteration, clusters with indices Z[i, 0] and Z[i, 1] are combined to form cluster n + i. A cluster with an index less than n corresponds to one of the n original observations. The distance between clusters Z[i, 0] and Z[i, 1] is given by Z[i, 2]. The fourth value Z[i, 3] represents the number of original observations in the newly formed cluster.
# 
# mehr infos: https://joernhees.de/blog/2015/08/26/scipy-hierarchical-clustering-and-dendrogram-tutorial/
# 

# In[327]:

#Z=pickle.load( open( "cluster_hierarchy_linkage_result.pickle", "rb" ) )




# ### going huge

# In[328]:

#
Z_huge=pickle.load( open( "cluster_hierarchy_linkage_result_without_name_clustering.pickle", "rb" ) )
uniqueSpatials=df3["spatialClean"].unique()
words=uniqueSpatials
len(words)


# In[329]:

df3[df3["dateClean"]=="764"]


# In[330]:

clusters=scipycluster.fcluster(Z_huge, t=0.07,criterion="distance")
clusters


# In[331]:

df3['spatialCluster'] = df3["spatialClean"].apply(getClusterID)
grp=df3.groupby("spatialCluster")
#print grp.groups.keys()
print "Number of clusters: %i" % len(grp.groups.keys())


# stichproben...

# In[332]:

grp.get_group(clusters[getWordIndex("Berlin")][0])


# In[333]:

grp.get_group(clusters[getWordIndex("Frankfurt, Main")][0])


# In[334]:

grp.get_group(clusters[getWordIndex("Frankfurt/Oder")][0])["spatialClean"].unique()


# In[335]:

grp.get_group(clusters[getWordIndex("Uri")][0])["spatialClean"].unique()


# In[336]:

grp.get_group(clusters[getWordIndex("Den Haag")][0])["spatialClean"].unique()


# a good time for inspecting our clusters' contents

# In[337]:

for key in grp.groups.keys():
    if key:
        print key
        print grp.get_group(key)["spatialClean"].unique()


# * synonym: ['Francofurti Ad Viadrum'] as a Latin translation of Frankfurt/Oder would be long to the cluster with ['Frankfurt/Main' 'Frankfurt/Oder' 'Frankfurt, Main' 'Frankfurt, O']
# * however, Frankfurt/Main and Frankfurt/Oder are to differt cities
# * ['Francofurti'] is in a 1-element cluster
# * ['C\xc3\xb6lln an der Spree'] is a synonym for Berlin
# * duplicate entries: ['Hallae Magdeburgicae  Hallae Magdeburgicae'] 1-gram und 2-gram vergleichen!
# * auf Enthaltensein von Berlin prüfen
# * St. Sankt Saint Bad als Präfix behandeln

# ## dealing with the clustering's results

# In[338]:

#s1="Frankfurt, O"
#s2='Hallae Magdeburgicae  Hallae Magdeburgicae'
#s3="Leipzig  Paris  Petersburg  London"
#s4='Franckfurt  N\xc3\xbcrnberg  Leipzig'
#s5='Freiburg i.Br. ' # not matched correctly but okay
#s6='Frankfurt/Main' 
#s7='Frankfurt, Main'

#s8='Bad Nauheim'
#s9='Rottach-Egern am Tegernsee'
#s10='Egern a. Tegernsee'
#s11="Plancy-L'Abbaye"
#s12='Bad Nauheim Sankt'
#s13="Saint Tropez"
#s14="Sankt Augustin"
#s15="Sankt-Augustin"
#s16="St.-Whatever"
#s17="St. Whatever"

def pickFirstCity(testString):
# checks if the testString contains multiple cities separated by whitespaces and returns the first city respecting city name prefixes such as Saint, St. etc.
    testString=unicode(testString,"utf-8")
    #print type(testString)
    #testString=testString.decode('unicode-escape')
    # matches for whitespaces that are NOT preceded by the following signs: ", ; : \ / " denoted in the regex by (?<!...)
    regex = re.compile("(?<![,;:\\\/])\s*",re.UNICODE)

    # matches various city prefix such as Saint etc.
    spatialPrefixRegExes=[]
    spatialPrefixRegExes.append(re.compile("^[Bb][Aa][Dd]\s*",re.UNICODE))
    spatialPrefixRegExes.append(re.compile("^[Ss][Aa][Nn][Kk][Tt][\s-]*",re.UNICODE))
    spatialPrefixRegExes.append(re.compile("^[Ss][Aa][Ii][Nn][Tt][\s-]*",re.UNICODE))
    spatialPrefixRegExes.append(re.compile("^[S][t]\.[\s-]*",re.UNICODE))
    spatialPrefixRegExes.append(re.compile("^[Dd][Ee][Nn]\s*",re.UNICODE))

    #print "Tested string: >%s<" % testString

    foundSpatialPrefix=False
    for i,r in enumerate(spatialPrefixRegExes):
        m = r.search(testString)
        if m:
            #print "Prefix %i" %i
            foundSpatialPrefix=True
    #print type(testString)
    m = regex.split(testString)

    if foundSpatialPrefix:
        if len(m)>1:
            return m[0]+" "+m[1]
    else:
        return m[0]

#print pickFirstCity(s2)    


# In[339]:

uniqueSpatials=df3["spatialClean"].unique()
beforeClusterClean=len(uniqueSpatials)
df3["spatialClean"]=df3["spatialClean"].apply(pickFirstCity)
df3


# In[340]:

uniqueSpatials=df3["spatialClean"].unique()
afterClusterClean=len(uniqueSpatials)
words=uniqueSpatials
#words
print "Before cluster cleaning: %i" % beforeClusterClean
print "After cluster cleaning: %i" % afterClusterClean


# In[341]:




# In[351]:

def d2(coord):
    #print "Altered d()"
    #print coord
    i, j = coord
    #print str(type(words[i]))+" : "+str(type(words[j]))
    if not type(words[i])==unicode:
        #print "bumm "+ str(words[i])
        if not words[i]:
            return 1
    if not type(words[j])==unicode:
        #print "bamm " + str(words[j])
        if not words[j]:
            return 1
    dist= 1- jaro_distance(words[i],words[j])
    print "%s vs. %s -> %f" %(words[i],words[j],dist)
    #return 1 - jaro_distance(unicode(str(words[i]), 'utf-8'), unicode(str(words[j]), 'utf-8'))
    return dist


# In[ ]:

r=np.triu_indices(afterClusterClean, 1)
r2=np.apply_along_axis(d2, 0, r)


# In[ ]:

Z=scipycluster.linkage(r2)
demoClustering=False
if not demoClustering:
    pickle.dump( Z, open( "cluster_hierarchy_linkage_result.pickle", "wb" ) )
    pickle.dump( r2, open( "r2.pickle", "wb" ) )


# In[ ]:

## load stuff
Z_huge=pickle.load( open( "cluster_hierarchy_linkage_result.pickle", "rb" ) )


# In[347]:

plt.figure(figsize=(25, 10))
plt.title('Hierarchical Clustering Dendrogram')
plt.xlabel('sample index')
plt.ylabel('distance')
scipycluster.dendrogram(
                        Z_huge,
                        leaf_rotation=90.,  # rotates the x axis labels
                        leaf_font_size=16.,  # font size for the x axis labels
                        )
plt.show()


# In[346]:

uniqueSpatials=df3["spatialClean"].unique()
words=uniqueSpatials
print len(words)
clusters=scipycluster.fcluster(Z_huge, t=0.01,criterion="distance")
clusters
df3['spatialCluster'] = df3["spatialClean"].apply(getClusterID)
grp=df3.groupby("spatialCluster")
#print grp.groups.keys()
print "Number of clusters: %i" % len(grp.groups.keys())

for key in grp.groups.keys():
    if key:
        print key
        print grp.get_group(key)["spatialClean"].unique()


# In[343]:

grp.get_group(clusters[getWordIndex("Frankfurt/Oder")][0])["spatialClean"].unique()


# In[ ]:



