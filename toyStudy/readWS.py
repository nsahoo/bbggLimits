#! /usr/bin/env python

#import os,sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import poisson 
from eff_sigma import getEffSigma

from ROOT import *
gROOT.SetBatch()

#
# Read the workspaces:
#

# These are the workspaces with photon correction fixed:
rooWsSig = TFile('hhbbgg.mH125_13TeV.inputsig.root')
rooWsBkg = TFile('hhbbgg.inputbkg_13TeV.root')

# These are bugged workspaces:
# rooWsSig = TFile('hhbbgg.mH125_13TeV.inputsig_bugged.root')
# rooWsBkg = TFile('hhbbgg.inputbkg_13TeV_bugged.root')


sigWs = rooWsSig.Get('w_all')
sigWs.Print()
bkgWs = rooWsBkg.Get('w_all')
bkgWs.Print()


mgg = sigWs.var('mgg')
mjj = sigWs.var('mjj')

# 
# Now, let's get the shape of the signal from the analysis workspace
# These shapes are from High-Mass High-Purity category (the most sensitive one):

pdfSig_mgg  = sigWs.pdf("mggSig_cat0_CMS_sig_cat2")
pdfSig_mjj  = sigWs.pdf("mjjSig_cat0_CMS_sig_cat2")
pdfSig_prod = sigWs.pdf("CMS_sig_cat2") # This is a product of the two PDFs above
sigDataSet  = sigWs.data("Sig_cat2")

print "\n Printout the parameters of the sig PDF"
l0 = RooArgSet(mgg,mjj)
pars = pdfSig_prod.getParameters(l0)
pars.Print()
parsiter = pars.createIterator()
var=parsiter.Next()
while var!=None:
    print '%s: %.3f  +/ %.3f'%(var.GetName(), var.getVal(), var.getError())
    var=parsiter.Next()


# Make some plots:
print 
c = TCanvas("c","c",0,0,900,600)
c.cd()

mgg.setRange('signal',118,135)
mjj.setRange('signal', 70,190)

mggFrame = mgg.frame(RooFit.Range("signal"))
sigDataSet.plotOn(mggFrame, RooFit.Binning(80))
pdfSig_mgg.plotOn(mggFrame, RooFit.Name("Sig_mgg"), RooFit.LineColor(kRed+1), RooFit.LineWidth(2))
mggFrame.Draw()
c.SaveAs('tmpfig_sig_mgg.png')


mjjFrame = mjj.frame(RooFit.Range("signal"))
sigDataSet.plotOn(mjjFrame, RooFit.Binning(30))
pdfSig_mjj.plotOn(mjjFrame, RooFit.Name("Sig_mjj"), RooFit.LineColor(kGreen+1), RooFit.LineWidth(2))
mjjFrame.Draw()
c.SaveAs('tmpfig_sig_mjj.png')


# Sigma_effectives times 2
dMgg = 2*getEffSigma(mgg, pdfSig_mgg, 110, 140)[0]
dMjj = 2*getEffSigma(mjj, pdfSig_mjj, 70, 190)[0]
#dMgg = 2*1.6
#dMjj = 2*18.3
print "Effective width:  mgg =", dMgg, "mjj =", dMjj

# 
# Now, let's get the shape of the background from the workspace
# 

mgg = bkgWs.var('mgg')
mjj = bkgWs.var('mjj')

pdfBkg_mgg = bkgWs.pdf("mggBkgTmpBer1_cat0_CMS_Bkg_cat2")
pdfBkg_mjj = bkgWs.pdf("mjjBkgTmpBer1_cat0_CMS_Bkg_cat2")
pdfBkg_prod = bkgWs.pdf("CMS_Bkg_cat2")
pdfBkg_mgg.Print()
pdfBkg_mjj.Print()

print "\n Printout the parameters of the bkg PDF"
l0 = RooArgSet(mgg,mjj)
pars = pdfBkg_prod.getParameters(l0)
pars.Print()
parsiter = pars.createIterator()
var=parsiter.Next()
while var!=None:
    print '%s: %.3f  +/ %.3f'%(var.GetName(), var.getVal(), var.getError())
    var=parsiter.Next()


realData = bkgWs.data("data_obs_cat2")


print 'Some checks'
#print pdfBkg_mgg.getVal(), pdfBkg_mgg.getVal(RooArgSet(mgg)), pdfBkg_mgg.getNorm()
#print pdfBkg_mjj.getVal(), pdfBkg_mjj.getVal(RooArgSet(mjj)), pdfBkg_mjj.getNorm()

mgg.setVal(125)
mjj.setVal(125)

print pdfBkg_mgg.getVal(), pdfBkg_mgg.getVal(RooArgSet(mgg)), pdfBkg_mgg.getNorm()
print pdfBkg_mjj.getVal(), pdfBkg_mjj.getVal(RooArgSet(mjj)), pdfBkg_mjj.getNorm()
# Results:
# 9.1609403468 0.0162331093879 1.0
# 6.4453044092 0.0072075547166 1.0


# Evaluating the PDFs at 125 GeV
N_data = realData.numEntries()
# print N_data
dNmgg = N_data*pdfBkg_mgg.getVal(RooArgSet(mgg))
dNmjj = N_data*pdfBkg_mjj.getVal(RooArgSet(mjj))

DeltaN = dNmgg*dNmjj*dMgg*dMjj

print 'Bkg PDF at 125:'
print '\t mgg=', dNmgg, 'mjj=', dNmjj, 'dN/{dm_gg*d_mjj} =', dNmgg*dNmjj
print "DeltaN = ", DeltaN, ", sqrt(DeltaN) =", np.sqrt(DeltaN)

# Results are:
#         mgg= 1.91550690777 mjj= 0.850491456559 dN/{dm_gg*d_mjj} = 1.62912226004
# DeltaN =  190.802799096 , sqrt(DeltaN) = 13.8131386403


# Would expect this guy to be equal to dNmgg*dNmjj, but it isnt:
# print "another check:", N_data*pdfBkg_prod.getVal(RooArgSet(mgg, mjj)), dNmgg*dNmjj


# From Pasqualle:
# UL = poisson_inv_cdf(mu=mu_bkg, p=95%)
for mu in [dNmgg*dMgg, dNmjj*dMjj, dNmgg*dNmjj*dMgg*dMjj]:
    UL = poisson.ppf(0.95, mu)
    print "UL from Poisson ppf = ", UL, 'for mu =', mu 


# Make a plot of backgrounds as well:
fakeData = pdfBkg_mgg.generate(RooArgSet(mgg), 120)

mggFrame = mgg.frame()
realData.plotOn(mggFrame, RooFit.Binning(80), RooFit.Name('data1'))
#fakeData.plotOn(mggFrame, RooFit.Binning(80), RooFit.Name('data1'))
pdfBkg_mgg.plotOn(mggFrame, RooFit.Name("Bkg_mgg"), RooFit.LineColor(kBlue), RooFit.LineWidth(2), RooFit.FillColor(kCyan-6))
mggFrame.Draw()

#func = mggFrame.findObject("Bkg_mgg")
#print "Eval from func =", func.Eval(125)

c.SaveAs('tmpfig_bkg.png')



