import ROOT
import array

class Variable:
    def __init__(self, name, formula, train=True):
        self.name = name
        self.formula = formula
        self.train = train
        self._mem = array.array('f', [0.])

    def makeBranch(self, tree):
        tree.Branch(self.name, self._mem, self.name+"/f")

    def checkTree(self, tree):
        fclass = ROOT.TTreeFormula(self.name, self.formula, tree)
        if fclass.GetNdim() == 1:
            return True
        print "Failed to make variable %s for %r" % (self.name, tree)
        return False

    def setTree(self, tree, fm):
        self._fclass = ROOT.TTreeFormula(self.name, self.formula, tree)
        fm.Add(self._fclass)

    def fill(self, instance):
        self._mem[0] = self._fclass.EvalInstance(instance)

    def val(self):
        return self._mem[0]


class BarrelIDConfig:
    name = "barrelPhotonID"
    trainingCut = "gedReco_pt>25 && abs(gedReco_eta)<1.4"
    trueCut = trainingCut + " && gedReco_iGen>=0 && gen_parentId[gedReco_iGen] == 25"
    varmap = [
        Variable("pt", "gedReco_pt", train=False),
        Variable("abseta", "abs(gedReco_eta)", train=False),
        Variable("isTrained", trainingCut, train=False),
        Variable("isTrue", trueCut, train=False),
        Variable("full5x5_sigmaIetaIeta", "gedReco_full5x5_sigmaIetaIeta"),
        Variable("full5x5_sigmaIetaIphi", "gedReco_full5x5_sigmaIetaIphi"),
        Variable("full5x5_sigmaIphiIphi", "gedReco_full5x5_sigmaIphiIphi"),
        Variable("hadTowOverEm", "gedReco_hadTowOverEm"),
        Variable("chargedHadronIso", "gedReco_chargedHadronIso"),
        Variable("neutralHadronIso", "gedReco_neutralHadronIso"),
        Variable("photonIso", "gedReco_photonIso"),
        Variable("hasPixelSeed", "gedReco_hasPixelSeed"),
    ]
    reweightvar1, reweightvar2, trainvar, truevar = varmap[0:4]
    hreweight_def = ROOT.TH2D("hreweight_def_barrel", "Bkg to signal reweight;Photon p_{T} (GeV);Photon |#eta|", 15, 25, 100, 4, 0., 1.4)


class EndcapIDConfig:
    name = "endcapPhotonID"
    trainingCut = "localReco_pt>25 && abs(localReco_eta)>1.5 && localReco_nLayers > 0 && localReco_depthCompatibility > -999."
    trueCut = trainingCut + " && localReco_iGen>=0 && gen_parentId[localReco_iGen] == 25"
    varmap = [
        Variable("pt", "localReco_pt", train=False),
        Variable("abseta", "abs(localReco_eta)", train=False),
        Variable("isTrained", trainingCut, train=False),
        Variable("isTrue", trueCut, train=False),
        Variable("sigmaUU", "localReco_sigmaUU"),
        Variable("sigmaVV", "localReco_sigmaVV"),
        Variable("nLayers", "localReco_nLayers"),
        Variable("firstLayer", "localReco_firstLayer"),
        Variable("FHoverE", "localReco_energyFH/localReco_energyEE"),
        Variable("depthCompatibility", "localReco_depthCompatibility"),
        Variable("isoRing0", "localReco_caloIsoRing0"),
        Variable("isoRing1", "localReco_caloIsoRing1"),
        Variable("isoRing2", "localReco_caloIsoRing2"),
        Variable("isoRing3", "localReco_caloIsoRing3"),
        Variable("isoRing4", "localReco_caloIsoRing4"),
    ]
    reweightvar1, reweightvar2, trainvar, truevar = varmap[0:4]
    hreweight_def = ROOT.TH2D("hreweight_def_endcap", "Bkg to signal reweight;Photon p_{T} (GeV);Photon |#eta|", 15, 25, 100, 2, 1.5, 3.)
