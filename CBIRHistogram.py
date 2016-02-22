import numpy as np
from scipy.spatial import distance

class CBIRHistogram:
    #no class variables for now
    
    def __init__(self,givenBitmap):
        self.histograms=[]
        self.bitmap=givenBitmap
        self.bitmapDataType=self.bitmap.dtype
        self.maxVal=np.iinfo(self.bitmapDataType).max
        self.countPixelComponents=self.bitmap.shape[2]
        self.isNormalized=False
        
        for i in range(self.countPixelComponents):
        # create an empty (i.e., filled with 0) array with maxVal elements
            hist=np.zeros(self.maxVal+1)
            self.histograms.append(hist)
    
    def calcHistogram(self):
        for row in self.bitmap:
            for col in row:
                for i,pixelComponent in enumerate(col):
                    self.histograms[i][pixelComponent]=self.histograms[i][pixelComponent]+1
        return self.histograms
    
    def normalizeHistograms(self):
        if not self.isNormalized:
            for histogram in self.histograms:
                for i,h in enumerate(histogram):
                    #print "Before: "+str(histogram[i])
                    m=histogram.max()
                    if m==0:
                        m=1
                    histogram[i]=float(h/m)
                    #print "After: "+str(histogram[i])
            self.isNormalized=True
        return self.histograms
    
    def distance(self,otherHistograms):
        distances=[]
        distSum=0
        for i,oHist in enumerate(otherHistograms):
            d=distance.cosine(self.histograms[i],oHist)
            distances.append(d)
            distSum=distSum+d
        return (distSum/len(distances),distances)