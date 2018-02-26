#!/usr/bin/env python

import os, math
import sys,getopt
from os.path import expandvars

from I3Tray import *
from icecube import icetray, dataclasses, dataio, toprec, recclasses
from icecube.icetray import I3Module
from icecube.dataclasses import I3EventHeader, I3Particle
from icecube.recclasses import I3LaputopParams

load("libgulliver")
load("liblilliput")

def laputop_migrad(tray, name):
    ########## SERVICES FOR GULLIVER ##########

    datareadoutName = "CleanedHLCTankPulses"
    excludedName = "ClusterCleaningExcludedStations"
    excludedTanksName = "ClusterCleaningExcludedTanks"  #<-- created on the fly!

    ## The "simple lambda" snowservice
    tray.AddService("I3SimpleSnowCorrectionServiceFactory","SimpleSnow21")(
        ("Lambda", 2.1)
        )

    ## This one is the standard one.
    tray.AddService("I3GulliverMinuitFactory","Minuit")(
        ("MinuitPrintLevel",-2),  
        ("FlatnessCheck",True),  
        #("Algorithm","SIMPLEX"),  
        ("Algorithm","MIGRAD"),  
        ("MaxIterations",1000),
        ("MinuitStrategy",2),
        ("Tolerance",0.01),    
        )

    tray.AddService("I3LaputopSeedServiceFactory","ToprecSeed")(
        ("InCore", "ShowerCOG"),
        ("InPlane", "ShowerPlane"),
        #("SnowCorrectionFactor", 1.5),   # Now obsolete
        ("Beta",2.6),                    # first guess for Beta
        ("InputPulses",datareadoutName)  # this'll let it first-guess at S125 automatically
    )

    fixcore = False   #always

    tray.AddService("I3LaputopParametrizationServiceFactory","ToprecParam2")(
        ("FixCore", fixcore),        
        ("FixTrackDir", True),
        ("IsBeta", True),
        ("MinBeta", 2.9),   ## From toprec... 2nd iteration (DLP, using beta)
        ("MaxBeta", 3.1),
        ("CoreXYLimits", 1000.0)
        )

    tray.AddService("I3LaputopParametrizationServiceFactory","ToprecParam3")(
        ("FixCore", fixcore),        
        ("FixTrackDir", False),      # FREE THE DIRECTION!
        ("IsBeta", True),
        ("MinBeta", 2.0),   ## From toprec... 3rd iteration (DLP, using beta)
        ("MaxBeta", 4.0),
        ("LimitCoreBoxSize", 15.0),
        ## Use these smaller stepsizes instead of the defaults:
        ("VertexStepsize",5.0),      # default is 20
        ("SStepsize", 0.045),        # default is 1
        ("BetaStepsize",0.15)        # default is 0.6    
        )

    tray.AddService("I3LaputopParametrizationServiceFactory","ToprecParam4")(
        ("FixCore", fixcore),        
        ("FixTrackDir", True),
        ("IsBeta", True),
        ("MinBeta", 1.5),   ## From toprec... 4th iteration (DLP, using beta)
        ("MaxBeta", 5.0),
        ("LimitCoreBoxSize", 15.0),
        ("MaxLogS125", 8.0),
        ## Use these smaller stepsizes instead of the defaults:
        ("VertexStepsize", 4.0),     # default is 20
        ("SStepsize", 0.045),        # default is 1
        ("BetaStepsize",0.15)        # default is 0.6 
        )

    tray.AddService("I3LaputopLikelihoodServiceFactory","ToprecLike2")(
        ("datareadout", datareadoutName),
        ("badtanks", excludedTanksName),
        ("dynamiccoretreatment",11.0),     # do the 11-meter core cut
        ("curvature",""),      # NO timing likelihood
        ("SnowServiceName","SimpleSnow21")
        )

    #**************************************************
    #    Adapt (old) BadStation list -> (new) BadTank list
    #    We need this because this is an old testscript, from
    #    before "BadStations" went obsolete
    #**************************************************
    class createBadTankList(icetray.I3Module):
        def __init__(self, context):
            icetray.I3Module.__init__(self, context)
            self.AddParameter('InputBadStationsName','Old BadStations name',0)
            self.AddParameter('OutputBadTanksName','New BadTanks name',0)
            self.AddOutBox("OutBox")
            
        def Configure(self):
            self.oldName = self.GetParameter('InputBadStationsName')
            self.newName = self.GetParameter('OutputBadTanksName')

        def Geometry(self, frame):
            if 'I3Geometry' in frame:
                geo = frame['I3Geometry']
                self.omg = geo.omgeo
            else:
                print 'No geometry found'
            self.PushFrame(frame,"OutBox")
        
        def Physics(self, frame):
            if self.oldName in frame:
                oldlist = frame[self.oldName]
                geo = frame["I3Geometry"]
                newlist = dataclasses.TankKey.I3VectorTankKey()   # startin' off empty!

                for station in oldlist:
                    ## put two entries (one for each tank) in the BadTanks list
                    newlist.append(dataclasses.TankKey(station, dataclasses.TankKey.TankA))
                    newlist.append(dataclasses.TankKey(station, dataclasses.TankKey.TankB))

                frame[self.newName] = newlist
            self.PushFrame(frame,"OutBox")


    tray.AddModule(createBadTankList,"convert_badlist")(
        ("InputBadStationsName", excludedName),
        ("OutputBadTanksName", excludedTanksName)
    )

    #**************************************************
    #                  The Laputop Fitter
    #**************************************************
    #tray.AddModule("I3LaputopFitter","Laputop")(
    tray.AddModule("I3LaputopFitter","LaputopMigrad")(
        ("SeedService","ToprecSeed"),
        ("NSteps",3),                    # <--- tells it how many services to look for and perform
        ("Parametrization1","ToprecParam2"),   # the three parametrizations
        ("Parametrization2","ToprecParam3"),
        ("Parametrization3","ToprecParam4"),
        ("StoragePolicy","OnlyBestFit"),
        ("Minimizer","Minuit"),
        ("LogLikelihoodService","ToprecLike2"),     # the three likelihoods
        ("LDFFunctions",["dlp","dlp","dlp"]),
        ("CurvFunctions",["","gausspar","gausspar"])   # VERY IMPORTANT : use time Llh for step 3, but fix direction!
        )
