import sys
import matplotlib.pyplot as plt
from scipy import signal
from spectutilio import *
import numpy as np
from math import sqrt

alpha = 2000.0 #sharpness
bin_size = 0.1 #Da
nbin = int((max_mz - min_mz)/bin_size)
halfL = int(nbin/2)
print( "bin_size=", bin_size, "nbin=", nbin )
xbin = np.linspace(min_mz, max_mz, nbin+1)

def gaussian(x, alpha, r):
  return np.exp(-alpha*np.power((x - r), 2.))

ref_spect = None
ref_tag = ""
lines = open(sys.argv[1], 'r').readlines()
for l in lines:
    es = l.strip().split()
    full_path = es[0]
    scan = int(es[1])
    peptide = es[2]
    file_name = full_path.split('/')[-1]
    file_type = file_name.split('.')[-1]
    file_name = file_name[:-len(file_type)-1]
    if file_type == "mgf":
        spectrum = get_spectrum_from_mgf( full_path, scan )
    elif file_type == "mzML":
        spectrum = get_spectrum_from_mzML( full_path, scan )
    elif file_type == "mzXML":
        spectrum = get_spectrum_from_mzXML( full_path, scan )
    else:
        print("Filetype not supported!")
        break

    print( "parsing", file_name, file_type, scan, peptide )
    draw_spect_pep_pdf( spectrum, peptide, "spect-"+file_name+"_"+str(scan)+".pdf" )

    if ref_tag == "":
        ref_tag = file_name+"_"+str(scan)
        spectrum.annotate_proforma(peptide, 0.5, "Da", ion_types="abyIm", neutral_losses={"H2O": -18.010565})
        ref_spect = spectrum
        mz_ref = spectrum.mz
        max_it = np.max(spectrum.intensity)
        it_ref = spectrum.intensity / max_it
        val0 = np.zeros([nbin+1])
        for center, h in zip(mz_ref, it_ref):
            val0 += sqrt(h) * gaussian(xbin, alpha, center)
    else:
        #compare with ref
        out_fn = ref_tag+"_"+file_name+"_"+str(scan)

        #mirror plot
        spectrum.annotate_proforma(peptide, 0.5, "Da", ion_types="abyIm", neutral_losses={"H2O": -18.010565})
        fig, ax = plt.subplots(figsize=(12, 6))
        sup.mirror(ref_spect, spectrum, ax=ax, spectrum_kws={'grid':False})
        plt.savefig("mirror-"+out_fn+".pdf", dpi=300, bbox_inches="tight", transparent=False)
        plt.close()

        #conv plot
        mz = spectrum.mz
        max_it = np.max(spectrum.intensity)
        it = spectrum.intensity / max_it
        #signal
        val = np.zeros([nbin+1])
        for center, h in zip(mz, it):
            val += sqrt(h) * gaussian(xbin, alpha, center)
        #correlate
        sig = signal.correlate(val0, val, mode='full')
        sig = sig[halfL:-halfL][::-1]
        x_mid = (min_mz+max_mz)/2
        #save
        with open( "corr-"+out_fn+".txt", 'w') as fp:
            for x, y in zip( xbin, sig ):
                fp.write( "%6.4f %6.4f\n" % (x-x_mid, y) )
        #draw
        plt.figure(21, figsize=(18, 6))
        plt.subplot(211)
        plt.plot(xbin-x_mid, sig, c='g')
        plt.subplot(223)
        plt.plot(xbin, val0, c='r')
        plt.subplot(224)
        plt.plot(xbin, val, c='b')
        plt.savefig("conv-"+out_fn+".pdf", dpi=300, bbox_inches="tight", transparent=False)
        plt.close()
        #top10
        for i in range(10):
            x_i = np.argmax(sig)
            x_p = xbin[x_i] - x_mid
            h_p = sig[x_i]
            sig[x_i] = 0.0
            print("top", i+1, "(%4.2f, %4.2f)"%(x_p, h_p))

    print( "Done!" )

