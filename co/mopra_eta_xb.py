#!/usr/bin/env python

from datetime import date
import matplotlib.pyplot as plt
import numpy as np

def midpt(d1, d2):
    return d1 + (d2 - d1)/2

# Mopra beam efficiency estimated for an extended source
# from Wong et al. (2011), Magellanic Mopra Assessment (MAGMA) paper
x = [midpt(date(2005, 5,29), date(2005,10,10)),
     midpt(date(2005,10,20), date(2005,10,29)),
     midpt(date(2006, 6,25), date(2006,10,27)),
     midpt(date(2007, 7,01), date(2007, 9,30)),
     midpt(date(2008, 6,19), date(2008, 6,29)),
     midpt(date(2008, 8,17), date(2008, 9,30)),
     midpt(date(2009, 6,15), date(2009, 9,30)),
     midpt(date(2010, 7,26), date(2010,10,10))]
y = [0.54, 0.38, 0.38, 0.45, 0.39, 0.48, 0.48, 0.43]

plt.plot(x,y,'o')
np.mean(y)
np.std(y)
