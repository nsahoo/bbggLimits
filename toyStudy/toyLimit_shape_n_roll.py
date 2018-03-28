#! /usr/bin/env python
import os,sys, argparse, time
import tempfile, getpass, subprocess
import numpy as np
import matplotlib.pyplot as plt

username = getpass.getuser()
from ROOT import *
gROOT.SetBatch()



c = TCanvas("c","c",0,0,900,600)
c.cd()

w = RooWorkspace("w")
w.factory('Gaussian::sig(x[100,180],mu[125],sigma[1])')
w.factory('Exponential::bkg(x,tau[-0.04])')
#w.factory('Chebychev::bkg(x,{-0.4,0.1})')
w.Print() 

x = w.var('x')
sigPdf    = w.pdf("sig")
bkgPdf    = w.pdf("bkg")
fakeData2 = bkgPdf.generate(RooArgSet(x), 120)
getattr(w,'import')(fakeData2,RooFit.Rename("data_obs"))

testFrame = x.frame()
fakeData2.plotOn(testFrame, RooFit.Binning(80), RooFit.Name('data2'))
bkgPdf.plotOn(testFrame, RooFit.Name("Bkg 2"), RooFit.LineColor(kBlue), RooFit.LineWidth(2), RooFit.FillColor(kCyan-6))
sigPdf.plotOn(testFrame, RooFit.Name("fake sig"), RooFit.LineColor(kRed+2), RooFit.LineWidth(2), RooFit.Normalization(0.10))
testFrame.Draw()

c.SaveAs('fig_gen_bkg.png')
    
w.writeToFile('ws.root')

Sigmas = np.array([0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 2.0])
Ns = np.array([100,120])
Ss = np.array([2, 4, 6])
toyCard2 = 'card_shape_n_roll.txt'


processes = []
for sw in Sigmas:     
    with open(toyCard2, 'r') as templateCard:
        tmpCard = templateCard.read()
        for si in Ss:
            for N in Ns:
                with tempfile.NamedTemporaryFile(dir='/tmp/'+username, prefix='toyCard_N'+str(N), suffix='.txt', delete=False) as card:
                    newCard = tmpCard.replace('%BKG%',str(N)).replace('%SIG%',str(si)).replace('%SW%',str(sw))
                    
                    card.write(newCard)
                    print card.name
                    pro = subprocess.Popen(['combine','-M','Asymptotic', '-m', '125','-n','_Shape_NBKG_'+str(N)+'_NSIG_'+str(si)+'_sw_'+str(sw), card.name])
                    processes.append(pro)
                    time.sleep(0.2)
                
                    
# Wait till all processes are finished:
for p in processes:
    print 'waiting for', p
    p.wait()



limsAll = {}
                
for si in Ss:
    for N in Ns:
        lims = []
        for sw in Sigmas:
            fname = 'higgsCombine_Shape_NBKG_'+str(N)+'_NSIG_'+str(si)+'_sw_'+str(sw)+'.Asymptotic.mH125.root'
            rfile = TFile(fname, 'READ')
            tree = rfile.Get("limit")
            tree.Draw("limit:quantileExpected", "", "goff")
            
            lims.append(tree.GetV1()[2])
            rfile.Close()
            # print si, N, sw,  lims[-1]
        limsAll['NBKG_'+str(N)+'_NSIG_'+str(si)] = lims

        #print 'Expected limit at r=0.5: ', lims
print limsAll


import itertools
marker = itertools.cycle((',', '+', '.', 'o', '*', '^'))

plt.clf()
for si in Ss:
    for N in Ns:
        plt.plot(np.sqrt(Sigmas), limsAll['NBKG_'+str(N)+'_NSIG_'+str(si)], marker = marker.next(), label='$N_{bkg} = '+str(N)+'; N_{sig} = '+str(si)+'$')
plt.axis([0.5, 2.5, 0, 8])
plt.title('Limits from toy shapes')
plt.xlabel(r'$\sqrt{\sigma_{eff}(signal)}}$')
plt.ylabel('Median expected Limit')
plt.legend()
plt.savefig('fig_scale_with_sigma.png')
