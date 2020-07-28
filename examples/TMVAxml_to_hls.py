# Imports to work with TMVA
import array
import ROOT
import xml.etree.ElementTree as ET
# Standard example imports
import conifer
import datetime
# Needed to get timestamp in python2.6
import time

def to_seconds(date):
    return time.mktime(date.timetuple())

def TMVA_reader(xml,input_varNames,input_var):
    reader = ROOT.TMVA.Reader()
    for name in input_varNames:
        reader.AddVariable(name,input_var[name])
    reader.BookMVA("BDT",xml)
    return reader

def TMVA_result(reader,input_varNames,input_var,input_varValues):
    y_TMVA = []
    for setOfValues in input_varValues:
        for iname,name in enumerate(input_varNames):
            input_var[name] = setOfValues[iname]
        y_TMVA.append(reader.EvaluateMVA("BDT"))
    return y_TMVA


TMVAxml = '/eos/cms/store/cmst3/user/evourlio/PF_L1_SelectionWeights/PhotonPionVsPU/MVAnalysis_BDT_reducedNTrees.weights.xml'
bdt = ET.parse(TMVAxml)

# Create a conifer config
cfg = conifer.backends.vivadohls.auto_config()
# Set the output directory to something unique
timestamp = to_seconds(datetime.datetime.now())
cfg['OutputDir'] = 'prj_{0}'.format(int(timestamp))

# Create and compile the model
model = conifer.model(bdt, conifer.converters.tmva, conifer.backends.vivadohls, cfg)
model.compile()

# Run HLS C Simulation and get the output
# TMVA BDT setup: Needs to be updated accordingly
input_varNames = ["fabs(eta)","coreShowerLength","maxLayer","sigmaPhiPhiTot"]
X = [[0.0,0.0,0.0,0.0]] # Just an example input to compare results
y_hls = model.decision_function(X)
input_var = {name : array.array('f',[0]) for name in input_varNames}
reader = TMVA_reader(TMVAxml,input_varNames,input_var)
y_TMVA = TMVA_result(reader,input_varNames,input_var,X)

# Synthesize the model
model.build()
