#!/usr/bin/env python

from ROOT import *
import argparse, os
from math import sqrt
from HiggsAnalysis.bbggLimits.NiceColors import *
import HiggsAnalysis.bbggLimits.CMS_lumi as CMS_lumi
from HiggsAnalysis.bbggLimits.MyCMSStyle import *
from HiggsAnalysis.bbggLimits.DefineScans import *

gROOT.SetBatch()

A13tev = [2.09078, 10.1517, 0.282307, 0.101205, 1.33191, -8.51168, -1.37309, 2.82636, 1.45767, -4.91761, -0.675197, 1.86189, 0.321422, -0.836276, -0.568156]

errUp =  7.293147e+00/100 # theoretical uncertainty on HH cross section from YR4
errDo =  8.408329e+00/100 # theoretical uncertainty on HH cross section from YR4


#coefxmin = (A13tev[0]+16*A13tev[2]+4*A13tev[6])
#Observed/Expected 3.07490022078 Th 3.0520579135 klambda -7.34
#Observed/Expected 4.29277026057 Th 4.33557538187 klambda 8.02
#coefxmin  kt = 0.411199557203*Lambda corresponds to the minimum of the cross section

def functionGF(kl,kt,c2,cg,c2g,A):
  return A[0]*kt**4 + A[1]*c2**2 + (A[2]*kt**2 + A[3]*cg**2)*kl**2 + A[4]*c2g**2 + ( A[5]*c2 + A[6]*kt*kl )*kt**2  + (A[7]*kt*kl + A[8]*cg*kl )*c2 + A[9]*c2*c2g  + (A[10]*cg*kl + A[11]*c2g)*kt**2+ (A[12]*kl*cg + A[13]*c2g )*kt*kl + A[14]*cg*c2g*kl

def Compare(th, exp):
  isless = 0
  Range = []
  for x in range(-1000,1000):
    xx = float(x)/50
    yexp = exp.Eval(xx)
    yth  =  th.Eval(xx)
    if yexp > yth and isless == 0:
      print 'Observed/Expected', yexp, 'Th', yth, 'klambda', xx
      isless = 1
      Range.append(xx)
    if yexp < yth and isless == 1:
      print 'Observed/Expected', yexp, 'Th', yth, 'klambda', xx
      isless = 0
      Range.append(xx)
    

parser =  argparse.ArgumentParser(description='Limit Tree maker')
parser.add_argument("limdir")
parser.add_argument('-u',"--unblind", dest="unblind", action='store_true', default=False)
parser.add_argument('-o', '--outFile', dest='outf', type=str, default="KLscanResult.root")
opt = parser.parse_args()

outfile = TFile(opt.limdir+'/'+opt.outf, 'RECREATE')

quantiles = ['0.025', '0.160', '0.500', '0.840', '0.975', '-1']
lims = {}
plots = {}
for qt in quantiles:
  lims[qt] = []
  plots[qt] = TGraphAsymmErrors()
  plots[qt].SetName('plot_'+qt.replace('.', 'p').replace("-", "m"))


myKl = []
notworked = open(opt.limdir+'/klscan_notworked.txt', 'w+')
for kl in scan_kl['kl']:
  #  fname = opt.limdir + '/HighMass_Node_SMkl' + str(kl).replace('.', 'p').replace('-', 'm') + '_kt1p0_cg0p0_c20p0_c2g0p0/datacards/higgsCombineHighMass_Node_SMkl' + str(kl).replace('.', 'p').replace('-', 'm') + '_kt1p0_cg0p0_c20p0_c2g0p0.Asymptotic.mH125.root'
  #fname = opt.limdir + '/CombinedCard_Node_SMkl' + str(kl).replace('.', 'p').replace('-', 'm') + '_kt1p0_cg0p0_c20p0_c2g0p0/higgsCombineCombinedCard_Node_SMkl' + str(kl).replace('.', 'p').replace('-', 'm') + '_kt1p0_cg0p0_c20p0_c2g0p0.Asymptotic.mH125.root'

  pointStr = ('kl_' + str(kl) + '_kt_1p0_cg_0p0_c2_0p0_c2g_0p0').replace('.', 'p').replace('-', 'm')
  fname = opt.limdir + '/CombinedCard_ARW_' + pointStr+'/higgsCombine_ARW_' + pointStr + '.Asymptotic.mH125_1.root'

  tfile = TFile(fname, "READ")
  if tfile.IsZombie() == 1:
    notworked.write(str(kl) + " 1.0 0.0 0.0 0.0 \n")
    continue
  tree = tfile.Get('limit')
  if tree == None:
    notworked.write(str(kl) + " 1.0 0.0 0.0 0.0 \n")
    continue
  myKl.append(kl)
  for qt in quantiles:
    tree.Draw("limit", "quantileExpected>"+str(float(qt)-0.001) + ' && quantileExpected < ' +str(float(qt)+0.001), "goff")
    lims[qt].append(tree.GetV1()[0])
  if lims['0.500'] == 0 or lims['-1'] == 0:
    notworked.write(str(kl) + " 1.0 0.0 0.0 0.0 \n")
    continue
  tfile.Close()


def kmax_finder(exp):

# for this algo we use the scaling property: 
#sigma = kt^4*(A0 + A2*(kl/kt)^2 + A6*(kl/kt))

  kmax = -100
  klist = []
  kl, sigma = Double(0), Double(0)
  for ikl,dummy in enumerate(myKl):
    exp.GetPoint(ikl,kl,sigma)
    s0 = 33.45*0.0026*functionGF(kl, 1, 0.0, 0.0, 0.0, A13tev)    
    kt = pow(sigma/s0, 1/4.)
    print 'kl ',kl, 'sigma ',sigma, ' kmax ', kmax 
    if kt > kmax:
      kmax = kt
      
  return kmax




nonresXSEC = TGraphAsymmErrors()
nonresXSEC.SetName("nonresXsec")
nonresXSEC_2 = TGraphAsymmErrors()
nonresXSEC_2.SetName("nonresXsec_2")
nonresXSEC_3 = TGraphAsymmErrors()
nonresXSEC_3.SetName("nonresXsec_3")
for ikl,kl in enumerate(myKl):
  xsec = 33.45*0.0026*functionGF(kl, 1.0, 0.0, 0.0, 0.0, A13tev)
  xsec_2 = 33.45*0.0026*functionGF(kl*2, 2, 0.0, 0.0, 0.0, A13tev)
#  xsec_3 = 33.45*0.0026*functionGF(kl, coefxmin*kl, 0.0, 0.0, 0.0, A13tev)
#  valkl = kl*kl*coefxmin
#  valkt = kl*coefxmin
  kmax = -100

  nonresXSEC.SetPoint(ikl, kl, xsec)
  nonresXSEC.SetPointError(ikl, 0,0, xsec*errDo, xsec*errUp)
  nonresXSEC_2.SetPoint(ikl, kl, xsec_2)
  nonresXSEC_2.SetPointError(ikl, 0,0, xsec_2*errUp, xsec_2*errDo)



  for qt in quantiles:
    if '-1' in qt:
      plots[qt].SetPoint(ikl, kl, lims['-1'][ikl])
#      print ikl, ' kl ', kl , ' lim ',  lims['-1'][ikl]
    else:
      plots[qt].SetPoint(ikl, kl, lims['0.500'][ikl])
  plots['0.160'].SetPointError(ikl, 0,0, lims['0.500'][ikl] - lims['0.160'][ikl], lims['0.840'][ikl] - lims['0.500'][ikl] ) 
  plots['0.025'].SetPointError(ikl, 0,0, lims['0.500'][ikl] - lims['0.025'][ikl], lims['0.975'][ikl] - lims['0.500'][ikl] ) 


kmax = kmax_finder(plots['-1'])
print 'kmax ', kmax

for ikl,kl in enumerate(myKl):
  xsec_3 = 33.45*0.0026*functionGF(kl*kmax, kmax, 0.0, 0.0, 0.0, A13tev)
  nonresXSEC_3.SetPoint(ikl, kl, xsec_3)
  nonresXSEC_3.SetPointError(ikl, 0,0, xsec_3*errDo, xsec_3*errUp)



SetGeneralStyle()
c = TCanvas("c", "c", 800, 600)
#c.SetGrid()
SetPadStyle(c)
#s2_col = kYellow
s2_col = kOrange #TColor.GetColor(NiceYellow2)
#s1_col = kGreen
s1_col = TColor.GetColor(NiceGreen2)
#th_col = kRed
th_col = TColor.GetColor(NiceRed)
th2_col = TColor.GetColor(NiceBlue)
ob_col = kBlack
#ob_col = TColor.GetColor(NiceBlueDark)

plots['0.025'].SetFillColor(s2_col)
plots['0.025'].SetLineColor(s2_col)
plots['0.160'].SetFillColor(s1_col)
plots['0.160'].SetLineColor(s1_col)
plots['0.500'].SetLineColor(cNiceBlueDark)
plots['0.500'].SetLineWidth(2)
plots['0.500'].SetLineStyle(kDashed)
plots['-1'].SetLineColor(ob_col)
plots['-1'].SetLineWidth(3)
nonresXSEC.SetLineColor(th_col)
nonresXSEC.SetFillColorAlpha(th_col, 0.5)
nonresXSEC_2.SetLineColor(cNicePurple)
nonresXSEC_2.SetFillColorAlpha(cNicePurple, 0.5)
nonresXSEC_3.SetLineColor(cNiceGreen)
nonresXSEC_3.SetFillColorAlpha(cNiceGreen, 0.5)
plots['0.025'].Draw("A3Z")

#plots['0.025'].GetXaxis().SetTitle('#kappa_{#lambda}/#kappa_{t}')
plots['0.025'].GetXaxis().SetTitle('#kappa_{#lambda}')
#plots['0.025'].GetYaxis().SetTitle('95% C.L. limit on #sigma(pp#rightarrowHH)#times#font[52]{B}(HH#rightarrowb#bar{b}#gamma#gamma) [fb]')
plots['0.025'].GetYaxis().SetTitle('#sigma(pp#rightarrowHH)#times#font[52]{B}(HH#rightarrow#gamma#gammab#bar{b}) [fb]')
plots['0.025'].SetMaximum(18)
plots['0.025'].GetXaxis().SetRangeUser(-20, 20)
SetAxisTextSizes(plots['0.025'])
c.Update()

plots['0.160'].Draw("3Z same")
plots['0.500'].Draw("LZ same")
if(opt.unblind): plots['-1'].Draw("CZ same")
nonresXSEC.Draw("3ZL same")
#nonresXSEC_2.Draw("3ZL same")
#nonresXSEC_3.Draw("3ZL same")

ltx = TLatex()
ltx.SetNDC()
ltx.SetTextAlign(32)
ltx.SetTextSize(.035)
ltx.DrawLatex(0.88,0.84,'#font[61]{pp#rightarrowHH#rightarrow#gamma#gammab#bar{b}}')

leg = TLegend(0.15, 0.59, 0.40, 0.88, "brNDC")
leg.SetTextSize(0.032)
#leg.SetFillColorAlpha(kWhite, 0.8)
leg.SetBorderSize(0)
leg.SetHeader("95% CL upper limits")#{#kappa_{t} = 1, c_{g} = c_{2g} = c_{2} = 0}")
leg.AddEntry(plots['-1'], 'Observed', 'l')
leg.AddEntry(plots['0.500'], 'Expected', 'l')
leg.AddEntry(plots['0.160'], 'Expected #pm 1 std. dev.', 'f')
leg.AddEntry(plots['0.025'], 'Expected #pm 2 std. dev.', 'f')
leg.Draw("same")

#CMS_lumi.lumi_13TeV = "35.87 fb^{-1}"
#CMS_lumi.writeExtraText = 1
#CMS_lumi.extraText = "Preliminary"
#CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
#CMS_lumi.CMS_lumi(c, 0,11)

latex = TLatex()
latex.SetNDC()
latex.SetTextSize(24)
latex.SetTextAlign(32)
latex.SetTextFont(43)
#latex.DrawLatex(0.89,.89,"#kappa_{t} = 1, c_{g} = c_{2g} = c_{2} = 0")
latex.DrawLatex(0.88,.74,"c_{g} = c_{2g} = c_{2} = 0")
latex.DrawLatex(0.88,.67,"#kappa_{t} = 1")
#latex.SetTextAlign(33)
#latex.SetTextSize(25)
#latex.SetTextAngle(-58)
#latex.SetTextColor(th_col)
#latex.DrawLatex(0.25,.45,"#kappa_{t} = 1")
latex.SetTextAngle(-82)
latex.SetTextColor(cNicePurple)
#latex.DrawLatex(0.50,.45,"#kappa_{t} = 2")

latex.SetTextAngle(-85)
latex.SetTextColor(cNiceGreen)
#latex.DrawLatex(0.55,.45,"#kappa_{t} = "+str("%.1f" % kmax))

c.Update()
c.cd()
c.Update()
c.RedrawAxis()

DrawCMSLabels(c, '35.9')

c.SaveAs(opt.limdir+'/'+opt.outf.replace(".root", ".pdf"))
c.SaveAs(opt.limdir+'/'+opt.outf.replace(".root", ".png"))

print 'Expected excluded range with kt = 1'
Compare(nonresXSEC, plots['0.500'])
print 'Expected excluded range with kt = 2'
Compare(nonresXSEC_2, plots['0.500'])
print 'Expected excluded kt_max'
Compare(nonresXSEC_3, plots['0.500'])

if(opt.unblind):
  print 'Observed excluded range with kt = 1'
  Compare(nonresXSEC, plots['-1'])
  print 'Observed excluded range with kt = 2'
  Compare(nonresXSEC_2, plots['-1'])
  print 'Expected excluded kt_max'
  Compare(nonresXSEC_3, plots['-1'])



outfile.cd()
for qt in quantiles:
  plots[qt].Write()

nonresXSEC.Write()
nonresXSEC_2.Write()


outfile.Close()


