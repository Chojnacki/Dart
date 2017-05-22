#!/usr/bin/python
# -*- coding: utf-8 -*-

# Second Year ENSTA Bretagne SPID Project
#    D : Brian Detourbet
#    A : Elouan Autret
#    A : Fahad Al Shaik
#    R : Corentin Rifflart
#    R : Clément Rodde
#    T : Rémi Terrien

# Code modified in May 2016, by BenBlop (small changes to conform with
#  new DART)

# Code modified in May 2017, by BenBlop (big changes to adapt to Irvin's
# drivers and to communicate with V-REP using sockets

# student starting code

import dart as d
import time
        


time.sleep(1)
myDart = d.Dart()
time.sleep(1)

myDart.stop()


