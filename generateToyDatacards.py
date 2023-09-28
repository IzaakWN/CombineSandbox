#! /usr/bin/env python3
# Author: Izaak Neutelings (September 2023)
# Inspiration: https://kcormi.github.io/HiggsAnalysis-CombinedLimit/tutorial2023_unfolding/unfolding_exercise/
import os
import ROOT; ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import gRandom, gROOT, gStyle, TFile, TH1F, TF1, TCanvas, TLegend,\
                 kBlack
gROOT.SetBatch(True)       # don't open GUI windows
gStyle.SetOptStat(False)   # don't make stat. box
gStyle.SetOptFit(1011)     # fit box
gStyle.SetOptTitle(False)  # don't make title on top of histogram
gRandom.SetSeed(123456789)


def ensuredir(dname,verb=0):
  """Make directory if it does not exist."""
  if dname and not os.path.exists(dname):
    if verb>=1:
      print(f">>> Making directory {dname}...")
    os.makedirs(dname)
  return dname
  

def joinpath(path,fname):
  """Join parent directory and filename."""
  return os.path.join(path,fname) if path else fname
  

def createhists_sig(nbins,xmin,xmax,nevts=1000,verb=0):
  print(">>> createhists_sig")
  """Generate signal histograms from gaussian pdf."""
  hists  = [ ]
  fsig   = TF1('fsig','gaus',xmin,xmax) # gaussian
  params = [ (0.5,25,3), (0.3,50,7), (0.2,70,10) ] # signal parameters
  for i, (frac,mu,sd) in enumerate(params,1):
    fsig.SetParameters(1.,mu,sd) # normalization, mean, width
    hname  = f"sig{i}"
    htitle = f"Signal {i}"
    hist   = TH1F(hname,htitle,nbins,xmin,xmax)
    hist.FillRandom("fsig",int(round(frac*nevts))) # generate histogram
    hists.append(hist)
  return hists
  

def createhists_bkg(nbins,xmin,xmax,nevts=1000,verb=0):
  """Generate background histogram from exponential pdf."""
  print(">>> createhists_bkg")
  hists = [ ]
  fbkg  = TF1('fbkg','expo',xmin,xmax) # exponential
  fbkg.SetParameters(0,-1./25.) # mean, offset
  hist  = TH1F("bkg", "Background",nbins,xmin,xmax) # generate histogram
  hist.FillRandom("fbkg",int(round(nevts)))
  hists.append(hist)
  return hists
  

def createhists_obs(hists,verb=0):
  """Generate toy data set from list of histograms."""
  print(">>> createhists_obs")
  nbins = hists[0].GetXaxis().GetNbins()
  xmin  = hists[0].GetXaxis().GetXmin()
  xmax  = hists[0].GetXaxis().GetXmax()
  hobs  = TH1F('data_obs','Observed',nbins,xmin,xmax) # toy dataset
  hobs.SetBinErrorOption(TH1F.kPoisson)
  for hist in hists:
    hobs.Add(hist)
  for i in range(nbins):
    yval = hobs.GetBinContent(i)
    yval = gRandom.Poisson(yval) # generate fluctuation
    hobs.SetBinContent(i,yval)
  hobs.SetLineColor(kBlack)
  hobs.SetLineWidth(2)
  hobs.SetMarkerColor(kBlack)
  hobs.SetMarkerStyle(8) # kFullDotLarge
  hobs.SetMarkerSize(0.6)
  return hobs
  

def plothists(hobs,hists,outdir="",verb=0):
  """Quick plot of histograms."""
  print(">>> plothists")
  fname = joinpath(outdir,"hists.png")
  canvas = TCanvas('canvas','canvas',100,100,800,600) # XYWH
  canvas.SetMargin(0.11,0.03,0.11,0.02) # LRBT
  ymax = 0
  for i, hist in enumerate(hists):
    hist.SetLineWidth(2)
    hist.SetLineColor(i+2)
    hist.Draw('HISTSAME')
    ymax = max(ymax,hist.GetMaximum())
  hobs.Draw('E1 PE0 SAME')
  hists[0].SetMaximum(1.1*max(ymax,hobs.GetMaximum()))
  hists[0].GetXaxis().SetTitle('x')
  hists[0].GetYaxis().SetTitle('Events / bin')
  hists[0].GetXaxis().SetLabelSize(0.052)
  hists[0].GetYaxis().SetLabelSize(0.052)
  hists[0].GetXaxis().SetTitleSize(0.055)
  hists[0].GetYaxis().SetTitleSize(0.055)
  hists[0].GetXaxis().SetTitleOffset(0.97)
  hists[0].GetYaxis().SetTitleOffset(1.00)
  legend = TLegend(0.60,0.94,0.88,0.70)
  legend.SetFillStyle(0)
  legend.SetBorderSize(0)
  legend.SetTextSize(0.056)
  legend.SetMargin(0.18)
  legend.SetTextFont(42)
  for hist in hists:
    legend.AddEntry(hist,hist.GetTitle(),'l')
  legend.AddEntry(hobs,hobs.GetTitle(),'lep')
  legend.Draw()
  canvas.SaveAs(fname)
  return canvas
  

def writehists(objs,subdir="cat1",outdir="",verb=0):
  """Write histograms to ROOT file."""
  print(f">>> writehists")
  ensuredir(outdir)
  fname  = joinpath(outdir,"hists.root")
  file   = TFile.Open(fname,'RECREATE')
  subdir = file.mkdir(subdir)
  subdir.cd()
  for obj in objs:
    if verb>=1:
      print(f">>> writehists: Writing {obj.GetName()}...")
    obj.Write(obj.GetName(),obj.kOverwrite)
  file.Close()
  return fname
  

def createdatacard(finname="hists.root",outdir="output",verb=0):
  """Create datacard txt file plus input histograms using CombineHarvester."""
  print(f">>> createdatacard")
  import CombineHarvester.CombineTools.ch as ch
  from CombineHarvester.CombineTools.ch import CombineHarvester, SystMap, CardWriter #, AutoRebin, SetStandardBinNames
  analysis = "toy"
  chans    = ['mm']
  eras     = ['Run2']
  cats     = ['cat1']
  cats     = list(enumerate(cats)) # map category name to (index,name) tuple
  masses   = ['125']
  procs = {
    'bkg': [ 'bkg' ],
    'sig': [ 'sig1', 'sig2', 'sig3' ],
  }
  harvester = CombineHarvester()
  harvester.AddObservations( ['*'], [analysis], eras, chans,               cats        )
  harvester.AddProcesses(    ['*'], [analysis], eras, chans, procs['bkg'], cats, False )
  harvester.AddProcesses(   masses, [analysis], eras, chans, procs['sig'], cats, True  )
  harvester.cp().AddSyst(harvester,'lumi','lnN',SystMap()(1.02))
  harvester.cp().AddSyst(harvester,'eff_m','lnN',SystMap()(1.02))
  harvester.cp().backgrounds().AddSyst(harvester,'norm_bkg','lnN',SystMap()(1.02))
  harvester.cp().ExtractShapes(finname,'$BIN/$PROCESS','$BIN/$PROCESS_$SYSTEMATIC')
  #harvester.cp().backgrounds().ExtractShapes(finname,'$BIN/$PROCESS','$BIN/$PROCESS_$SYSTEMATIC')
  #harvester.cp().signals().ExtractShapes(finname,'$BIN/$PROCESS$MASS','$BIN/$PROCESS$MASS_$SYSTEMATIC')
  ###SetStandardBinNames(harvester,"$CHANNEL_$BIN_$ERA")
  ###rebinner = AutoRebin().SetBinThreshold(0.0).SetBinUncertFraction(0.20).SetRebinMode(1).SetPerformRebin(True).SetVerbosity(0)
  harvester.SetGroup('sys',["^((?!bin).)*$"]) # everything except bin-by-bin
  if verb>=1:
    harvester.PrintObs().PrintProcs().PrintSysts()
  ###harvester.AddDatacardLineAtEnd("* autoMCStats %d 0 1"%(threshold)) # [channel] autoMCStats [threshold] [include-signal = 0] [hist-mode = 1]
  dcname = joinpath(outdir,"datacard.txt")
  writer = CardWriter("$TAG/datacard.txt","$TAG/datacard.input.root") #"$ANALYSIS_$CHANNEL_$BINID_$ERA-$MASS.txt"
  writer.CreateDirectories(True).SetVerbosity(verb)
  writer.WriteCards(outdir,harvester)
  ###writer.SetWildcardMasses([ ])
  ###writer.WriteCards(outdir,harvester.bin())
  ###rootfile = TFile("datacard.root",'RECREATE')
  ###harvester.cp().WriteDatacard("datacard.txt",rootfile)
  return dcname
  

def createworkspace(dcname,wsname,outdir="",verb=0):
  """Make workspace with text2workspace.py."""
  print(f">>> createworkspace")
  wsname = joinpath(outdir,wsname)
  cmd = f"text2workspace.py -m 125 {dcname} -o {wsname} "+\
         "-P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel "+\
         "--PO verbose --PO json=physOpts.json"
  print(f">>> createworkspace: Executing {cmd!r}...")
  os.system(cmd)
  return wsname
  

def mdfit(wsname,verb=0):
  """Make workspace with text2workspace.py."""
  print(f">>> mdfit")
  cmd = f"combineTool.py -M MultiDimFit -d {wsname} "+\
        " --setParameters r_sig1=1,r_sig2=1,r_sig3=1 --redefineSignalPOIs r_sig1,r_sig2,r_sig3"
  print(f">>> createworkspace: Executing {cmd!r}...")
  os.system(cmd)
  return wsname
  

def main(args):
  nevts  = 5e3
  nbins, xmin, xmax = 50, 0, 100
  indir  = "input"
  outdir = "output"
  hists  = [ ]
  hists += createhists_sig(nbins,xmin,xmax,nevts=0.4*nevts,verb=args.verbosity)
  hists += createhists_bkg(nbins,xmin,xmax,nevts=0.6*nevts,verb=args.verbosity)
  hobs   = createhists_obs(hists,verb=args.verbosity)
  canvas = plothists(hobs,hists,outdir=indir,verb=args.verbosity)
  fname  = writehists([canvas,hobs]+hists,outdir=indir,verb=args.verbosity)
  canvas.Close()
  dcname = createdatacard(fname,outdir=outdir,verb=args.verbosity)
  wsname = createworkspace(dcname,"workspace.root",outdir=outdir,verb=args.verbosity)
  mdfit(wsname,verb=args.verbosity)
  

if __name__ == "__main__":
  from argparse import ArgumentParser
  description = """Simple plotting script for pico analysis tuples"""
  parser = ArgumentParser(prog="plot",description=description,epilog="Good luck!")
  parser.add_argument('-v', '--verbose', dest='verbosity', type=int, nargs='?', const=1, default=0, action='store',
                                         help="set verbosity" )
  args = parser.parse_args()
  main(args)
  print(">>> Done.")
  
