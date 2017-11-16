import FWCore.ParameterSet.Config as cms

from RecoEgamma.EgammaTools.hgcalElectronIDValueMap_cfi import hgcalElectronIDValueMap
from RecoEgamma.EgammaTools.hgcalPhotonIDValueMap_cfi import hgcalPhotonIDValueMap
from RecoEgamma.Phase2InterimID.hgcalElectronMVAProducer_cfi import hgcalElectronMVA
from RecoEgamma.Phase2InterimID.hgcalPhotonMVAProducer_cfi import hgcalPhotonMVA

# Make sure all of these are in path or task
hgcElectronID = hgcalElectronIDValueMap.clone()
hgcPhotonID = hgcalPhotonIDValueMap.clone()
hgcElectronMVAbarrel = hgcalElectronMVA.clone(electrons=cms.InputTag("gedGsfElectrons"))
hgcElectronMVAendcap = hgcalElectronMVA.clone(electrons=cms.InputTag("ecalDrivenGsfElectronsFromMultiCl"))
hgcPhotonMVAbarrel = hgcalPhotonMVA.clone(photons=cms.InputTag("gedPhotons"))
hgcPhotonMVAendcap = hgcalPhotonMVA.clone()

phase2EgammaTask = cms.Task(
    hgcElectronID,
    hgcPhotonID,
    hgcElectronMVAbarrel,
    hgcElectronMVAendcap,
    hgcPhotonMVAbarrel,
    hgcPhotonMVAendcap,
)

# Caution: won't work in scheduled mode!
phase2Egamma = cms.Sequence(phase2EgammaTask)
