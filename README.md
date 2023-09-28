# CombineSandbox

For testing some development of combine.

## Installation
Get combine by follow the [instructions for developers](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/#for-developers).

At the time of writing, get CMSSW:
```
source $VO_CMS_SW_DIR/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc900
cmsrel CMSSW_11_3_4
cd CMSSW_11_3_4/src
cmsenv
```
Install latest combine:
```
git clone git@github.com:cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
```
_or_, get my development, e.g.
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
git clone git@github.com:IzaakWN/CombineSandbox.git HiggsAnalysis/CombineSandbox
```
Finally, compile
```
scramv1 b clean; scramv1 b -j10
```

## Scripts
The `generateToyDatacards.py` script creates a simple toy analysis with multiple signal to test the multi-signal physics model.
1. It creates a ROOT file with input histograms for datacards.
2. It creates a simple datacard file `output/datacard.txt` with `CombineHarvester`.
2. It creates a workspace from the datacard file with the `MultiSignalModel` physics model.
2. It fits the workspace with the `MultiDimFit` method.
```
./generateToyDatacards.py
```

You can create the workspace yourself with
```
text2workspace.py -m 125 output/datacard.txt -o output/workspace.root -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose --PO json=physOpts.json
```
and fit with
```
combineTool.py -M MultiDimFit -d output/workspace.root --setParameters r_sig1=1,r_sig2=1,r_sig3=1 --redefineSignalPOIs r_sig1,r_sig2,r_sig3
```

<p align="center" vertical-align: middle>
  <img src="../docs/hists.png" alt="Toy analysis" width="450" hspace="20"/>
</p>