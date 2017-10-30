import ROOT
import array
import glob
import math
import re
import sys
import bdtCommon

def makeROC(trees, cuts, truecut, bkgcut, bkgPerEvent=True):
    x, y, exl, exh, eyl, eyh = map(lambda _: array.array('d', [0.]*len(cuts)), xrange(6))

    hdummy = ROOT.TH1D("dummy", "", 2, 0, 2)
    for i, cut in enumerate(cuts):
        hdummy.Reset()
        for tree in trees:
            tree.Draw("(%s) >>+dummy" % cut, truecut, "goff")
        nPass, nAll = hdummy.GetBinContent(2), hdummy.Integral()
        y[i] = nPass / nAll
        eyl[i] = y[i] - ROOT.TEfficiency.ClopperPearson(nAll, nPass, 0.68, False)
        eyh[i] = ROOT.TEfficiency.ClopperPearson(nAll, nPass, 0.68, False) - y[i]

    nevents = 0.
    for i, cut in enumerate(cuts):
        hdummy.Reset()
        for tree in trees:
            tree.Draw("(%s) >>+dummy" % cut, bkgcut, "goff")
            nevents += tree.GetEntries()
        nPass, nAll = hdummy.GetBinContent(2), hdummy.Integral()
        if bkgPerEvent:
            x[i] = nPass / nevents
            exl[i] = x[i] - ROOT.TEfficiency.ClopperPearson(nAll, nPass, 0.68, False) * nAll / nevents
            exh[i] = ROOT.TEfficiency.ClopperPearson(nAll, nPass, 0.68, False) * nAll / nevents - x[i]
        else:
            x[i] = nPass / nAll
            exl[i] = x[i] - ROOT.TEfficiency.ClopperPearson(nAll, nPass, 0.68, False)
            exh[i] = ROOT.TEfficiency.ClopperPearson(nAll, nPass, 0.68, False) - x[i]

    gROC = ROOT.TGraphAsymmErrors(len(cuts), x, y, exl, exh, eyl, eyh)
    gROC.GetXaxis().SetTitle("Background / Event" if bkgPerEvent else "Background Efficiency")
    gROC.GetYaxis().SetTitle("Signal Photon Efficiency")
    gROC.SetMarkerSize(0.6)
    gROC.SetLineWidth(2)
    #gROC.SetLineStyle(ROOT.kDashed)
    return gROC


def makeEff(trees, histDef, ncut, dcut):
    htmpnum = histDef.Clone("tmpnum")
    htmpdenom = histDef.Clone("tmpdenom")
    for tree in trees:
        tree.Draw(histDef.GetTitle()+">>tmpnum", "(%s)&&(%s)" % (dcut, ncut), "goff")
        tree.Draw(histDef.GetTitle()+">>tmpdenom", "%s" % dcut, "goff")
    hEff = ROOT.TEfficiency(htmpnum, htmpdenom)
    return hEff

filenames = ["/data/ncsmith/932phoID_round2/GJets13TeV.root"]
files = map(ROOT.TFile.Open, filenames)
trees = [f.Get("ntupler/photons") for f in files]


# https://twiki.cern.ch/twiki/bin/viewauth/CMS/CutBasedPhotonIdentificationRun2
EAs = [
    ["(1.0  <=abs(gedReco_eta)) ?",  "0.0377",  "0.0807",  "0.1107"],
    ["(1.479<=abs(gedReco_eta)) ?",  "0.0306",  "0.0629",  "0.0699"],
    ["(2.0  <=abs(gedReco_eta)) ?",  "0.0283",  "0.0197",  "0.1056"],
    ["(2.2  <=abs(gedReco_eta)) ?",  "0.0254",  "0.0184",  "0.1457"],
    ["(2.3  <=abs(gedReco_eta)) ?",  "0.0217",  "0.0284",  "0.1719"],
    ["(2.4  <=abs(gedReco_eta)) ?",  "0.0167",  "0.0591",  "0.1998"], 
    ["",                             "0.0360",  "0.0597",  "0.1210"],
]
chgIso = ":".join(["%s max(gedReco_chargedHadronIso - rho*%s,0.)" % (ea[0], ea[1]) for ea in EAs])
neuIso = ":".join(["%s max(gedReco_neutralHadronIso - rho*%s,0.)" % (ea[0], ea[2]) for ea in EAs])
phoIso = ":".join(["%s max(gedReco_photonIso        - rho*%s,0.)" % (ea[0], ea[3]) for ea in EAs])
run2WPs_barrel = [
    'gedReco_passElectronVeto && gedReco_full5x5_sigmaIetaIeta < 0.01031 && gedReco_hadronicOverEm < 0.0597 && ({chgIso}) < 1.295 && ({neuIso}) < 10.910+0.0148*gedReco_pt+0.000017*gedReco_pt^2 && ({phoIso}) < 3.630+0.0047*gedReco_pt'.format(chgIso=chgIso, neuIso=neuIso, phoIso=phoIso),
    'gedReco_passElectronVeto && gedReco_full5x5_sigmaIetaIeta < 0.01022 && gedReco_hadronicOverEm < 0.0396 && ({chgIso}) < 0.441 && ({neuIso}) <  2.725+0.0148*gedReco_pt+0.000017*gedReco_pt^2 && ({phoIso}) < 2.571+0.0047*gedReco_pt'.format(chgIso=chgIso, neuIso=neuIso, phoIso=phoIso),
    'gedReco_passElectronVeto && gedReco_full5x5_sigmaIetaIeta < 0.00994 && gedReco_hadronicOverEm < 0.0269 && ({chgIso}) < 0.202 && ({neuIso}) <  0.264+0.0148*gedReco_pt+0.000017*gedReco_pt^2 && ({phoIso}) < 2.362+0.0047*gedReco_pt'.format(chgIso=chgIso, neuIso=neuIso, phoIso=phoIso),
]
run2WPs_endcap = [
    'gedReco_hasPixelSeed && gedReco_full5x5_sigmaIetaIeta < 0.03013 && gedReco_hadronicOverEm < 0.0481 && ({chgIso}) < 1.011 && ({neuIso}) <  5.931+0.0163*gedReco_pt+0.000014*gedReco_pt^2 && ({phoIso}) < 6.641+0.0034*gedReco_pt'.format(chgIso=chgIso, neuIso=neuIso, phoIso=phoIso),
    'gedReco_hasPixelSeed && gedReco_full5x5_sigmaIetaIeta < 0.03001 && gedReco_hadronicOverEm < 0.0219 && ({chgIso}) < 0.442 && ({neuIso}) <  1.715+0.0163*gedReco_pt+0.000014*gedReco_pt^2 && ({phoIso}) < 3.863+0.0034*gedReco_pt'.format(chgIso=chgIso, neuIso=neuIso, phoIso=phoIso),
    'gedReco_hasPixelSeed && gedReco_full5x5_sigmaIetaIeta < 0.03000 && gedReco_hadronicOverEm < 0.0213 && ({chgIso}) < 0.034 && ({neuIso}) <  0.586+0.0163*gedReco_pt+0.000014*gedReco_pt^2 && ({phoIso}) < 2.617+0.0034*gedReco_pt'.format(chgIso=chgIso, neuIso=neuIso, phoIso=phoIso),
]
run2WPs_endcap = [wp.replace("gedReco_", "localReco_") for wp in run2WPs_endcap]

fout = ROOT.TFile.Open("plots_cuts_pix.root", "recreate")

# ROC curves
rocBarrel = makeROC(trees[0:1], run2WPs_barrel, bdtCommon.BarrelIDConfig.trueCut, bdtCommon.BarrelIDConfig.bkgCut)
rocBarrel.SetNameTitle("barrelCutsROC", "Run II cuts (PU 25)")
rocBarrel.Write()
rocEndcap = makeROC(trees[0:1], run2WPs_endcap, bdtCommon.EndcapIDConfigRun2.trueCut, bdtCommon.EndcapIDConfigRun2.bkgCut)
rocEndcap.SetNameTitle("endcapCutsROC", "Run II cuts (PU 25)")
rocEndcap.Write()

