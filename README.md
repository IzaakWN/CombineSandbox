# CombineSandbox

For testing some development of combine.

## Installation
Get combine by follow the [instructions for developper](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/#for-developers).

At the time of writing, get CMSSW:
```
cmsrel CMSSW_11_3_4
cd CMSSW_11_3_4/src
cmsenv
```
Install latest combine:
```
git clone git@github.com:cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
```
or get my development, e.g.
```
git clone git@github.com:IzaakWN/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
git checkout addPOsFromJSON
```
Install `CombineHarvester`:
```
cd $CMSSW_BASE/src/
bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/main/CombineTools/scripts/sparse-checkout-https.sh)
```
Install this repository:
```
git clone git@github.com:IzaakWN/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombineSandbox
```

## Scripts
The `generateToyDatacards.py` script creates a simple toy analysis with multiple signal to test the multi-signal physics model.
1. It creates a ROOT file with input histograms for datacards.
2. It creates a simple data file `output/datacard.txt` with `CombineHarvester`.
```
./generateToyDatacards.py
```
Now create a workspace with
```
text2workspace.py -m 125 output/datacard.txt -o output/workspace.root -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose --PO json=physOpts.json
```