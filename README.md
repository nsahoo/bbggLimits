# bbggLimits
Package for computing limits for the Run II analyses

### Instalation
First, setup the environment with the Higgs Combine tools: https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideHiggsAnalysisCombinedLimit#For_end_users_that_don_t_need_to   
Currently recommended CMSSW version: 71X
```
setenv SCRAM_ARCH slc6_amd64_gcc481
cmsrel CMSSW_7_1_5 ### must be a 7_1_X release  >= 7_1_5;  (7.0.X and 7.2.X are NOT supported either) 
cd CMSSW_7_1_5/src 
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v5.0.2   # try v5.0.1 if any issues occur
scramv1 b clean; scramv1 b # always make a clean build, as scram doesn't always see updates to src/LinkDef.h

```    
Get bbggLimits:   
```
cd ${CMSSW_BASE}/src/HiggsAnalysis/
git clone git@github.com:ResonantHbbHgg/bbggLimits.git
cd bbggLimits
#scramv1 b -j 10
./Compile.sh
```
   
### Make Limits Trees
```
LimitTreeMaker -i <input list of files> -o <output location> [optional: -min <min mtot> -max <max mtot> -scale <scale factor> -photonCR (do photon control region) -KF (use Mtot_KF to cut on mass window) -MX (use MX to cut on mass window) (choose either -MX or -KF!)
```   
*-min and max*: use it to cut on the 4-body invariant mass;   
*-scale*: set this to the scale factor to be multiplied to normalize your input file, for example xsec*lumi/(sum of weights);   
*-photonCR*: use this flag to use data from photon control region (one photon fails the ID requirements);   
*-KF or -MX*: cut on kinematic fitted 4body mass (KF) or on the MX variable (MX)   

### How to run it :
```
1) Edit your .json ( example in LimitSetting/jest.json ) :
	If you want to change the value of "minMggMassFit" "maxMggMassFit" ... etc for one Mass in particular just add the line in "signal":	
"param_Mass" :[minMggMassFit,maxMggMassFit,minMjjMassFit,maxMjjMassFit,minSigFitMgg,maxSigFitMgg,minSigFitMjj,maxSigFitMjj,minHigMggFit,maxHigMggFit,minHigMjjFit,maxHigMjj],
If you want to run runCombine and BrazilianFlag at the same time than bbgg2DFit, just put runCombine and doBrazilianFlag accordingly.

2) Run bbgg2DFit MyJsonFile MyFolder
	MyJsonFile is the Json file you have created 
	MyFolder is the name of the folder in witch bbgg2DFit runCombine and BrazilianFlag will put all their outputs. 
	The name of the directory will be MyFolder_v{version} with {version} the number provided in MyJsonFile
	If you don't provide MyFolder argument bbgg2DFit will create bbggToolsResults_v{version} by default.

3) If you want to run RunCombine and/or BrazilianFlag alone run :
	runCombine MyJsonFile MyFolder
	BrazilianFlag MyJsonFile MyFolder
```         
