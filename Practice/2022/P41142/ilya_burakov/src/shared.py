import pandas as pd 
from rdflib import Namespace

chp = Namespace("http://iburakov.me/ontologies/chord-progressions#")
chpv = Namespace("http://iburakov.me/ontologies/chord-progressions/void#")

def read_songs(inp):
	df = pd.read_csv(inp)
	for c in "chordAbs", "chordRel":
	    df[c] = df[c].apply(lambda x: eval(x))
	return df
