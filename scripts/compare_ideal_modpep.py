import sys
import matplotlib.pyplot as plt
from scipy import signal
from spectutilio import *
import numpy as np
from math import sqrt, fabs
from spectrum_utils import fragment_annotation as fa, proforma
from ms2pip.single_prediction import SinglePrediction

alpha = 2000.0  #sharpness
bin_size = 0.01 #Da
nbin = int((max_mz - min_mz)/bin_size)
halfL = int(nbin/2)
print( "bin_size=", bin_size, "nbin=", nbin )
xbin = np.linspace(min_mz, max_mz, nbin+1)

def gaussian(x, alpha, r):
  return np.exp(-alpha*np.power((x - r), 2.))

# generate ref spectrum, ions with modification
# PEPT*IDE
# PEPT*, PEPT*I, PEPT*ID
# T*IDE, PT*IDE, EPT*IDE

#usage: file scan peptide

full_path = sys.argv[1]
scan = int(sys.argv[2])
peptide = sys.argv[3]

#generate ideal fragments
modpeptide = peptide.replace("*", "[+5000]") #digital labeling
prots = proforma.parse(modpeptide)
#keep first
#frags = fa.get_theoretical_fragments( prots[0], "abyIm", neutral_losses={"H2O": -18.010565} ) #
#frags = fa.get_theoretical_fragments( prots[0], "by" ) #, neutral_losses={"H2O": -18.010565}
frags = fa.get_theoretical_fragments( prots[0], "aby" ) #, neutral_losses={"H2O": -18.010565}

std_mz = []
mod_mz = []
for tag, mz in frags:
    if mz > 5000:
        mod_mz.append(mz - 5000)
    else:
        std_mz.append(mz)

#generate predicted intensity with ms2pip
ms2pip_sp = SinglePrediction()
pred_mz, pred_int, _ = ms2pip_sp.predict(peptide.replace("*", ""), "-", 2, model="CID")
#match intensity with mod
max_i = np.max( pred_int )
min_i = np.min( pred_int )
scale = 2.0 #
tol = 1e-6
std_int = []
for mz in std_mz:
    d2 = [(m-mz)**2 for m in pred_mz]
    ndx = np.argmin(d2)
    min_d2 = d2[ndx]
    if min_d2 < tol:
        hit_int = pred_int[ndx]
    else:
        #should be a ion
        hit_int = max_i/10.0
    if hit_int < max_i/scale:
        hit_int = max_i/scale
    std_int.append(hit_int)
mod_int = []
for mz in mod_mz:
    d2 = [(m-mz)**2 for m in pred_mz]
    ndx = np.argmin(d2)
    min_d2 = d2[ndx]
    if min_d2 < tol:
        hit_int = pred_int[ndx]
    else:
        #should be a ion
        hit_int = max_i/10.0
    if hit_int < max_i/scale:
        hit_int = max_i/scale
    mod_int.append(hit_int)

#print(std_mz)
#print(mod_mz)
val_std = np.zeros([nbin+1])
for center, h in zip(std_mz, std_int):
    val_std += h/max_i * gaussian(xbin, alpha, center)
val_mod = np.zeros([nbin+1])
for center, h in zip(mod_mz, mod_int):
    val_mod += h/max_i * gaussian(xbin, alpha, center)

#read MS2 file
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

#conv plot for exp MS2
mz = spectrum.mz
#max_it = np.max(spectrum.intensity)
sorted_it = sorted(spectrum.intensity, reverse=True)
top1 = sorted_it[0]
top2 = sorted_it[1]
top3 = sorted_it[2]
max_it = top3
raw_it = spectrum.intensity / max_it
#cap
it = [1.0 if i>1 else i for i in raw_it]
val = np.zeros([nbin+1])
for center, h in zip(mz, it):
    #hack, sqrt, log, linear?
    val += sqrt(h) * gaussian(xbin, alpha, center)

#correlate
x_mid = (min_mz+max_mz)/2

#for standard ion, make sure peptide match MS2
sig_std = signal.correlate(val, val_std, mode='full')
sig_std = sig_std[halfL:-halfL][::-1]
x_i = np.argmax(sig_std)
if x_i != halfL:
    print(x_i-halfL)
    print("Warning! check the peptide, it does not match with the MS2")
else:
    print("Peptide fit!")

#remove std mz from "val"
clean_val = [ 0 if b>tol else a for a, b in zip( val, val_std ) ]
#sig_mod = signal.correlate(val, val_mod, mode='full')
sig_mod = signal.correlate(clean_val, val_mod, mode='full')
sig_mod = sig_mod[halfL:-halfL][::-1]

#draw
plt.figure(21, figsize=(18, 6))
plt.subplot(211)
plt.plot(xbin-x_mid, sig_std, c='g')
plt.subplot(212)
plt.plot(xbin-x_mid, sig_mod, c='g')
plt.savefig("conv-"+file_name+"_"+str(scan)+".pdf", dpi=300, bbox_inches="tight", transparent=False)
plt.close()

##global
x_i = np.argmax(sig_mod)
h_p = sig_mod[x_i]
x_p = xbin[x_i] - x_mid
print("global_shift", "(%4.2f, %4.2f)"%(-x_p, h_p))
##top10
shift = []
for i in range(20):
    #loc positive only?
    #x_i = np.argmax(sig_mod)
    x_i = np.argmax(sig_mod[:halfL])
    #mz
    x_p = xbin[x_i] - x_mid
    shift.append(x_p)
    h_p = sig_mod[x_i]
    h_p0 = sig_std[x_i]
    sig_mod[x_i] = 0.0
    print("top", i+1, "(%4.2f, %4.2f, %4.2f)"%(-x_p, h_p, h_p0))

final_shift = -shift[0]
if final_shift<0:
    mod_str = "[" + "%4.2f"%final_shift + "]"
else:
    mod_str = "[+" + "%4.2f"%final_shift + "]"

#print(mod_str)
modpeptide = peptide.replace("*", mod_str) #digital labeling
print( "output", file_name, file_type, scan, modpeptide )
draw_spect_pep_pdf( spectrum, modpeptide, "spect-"+file_name+"_"+str(scan)+".pdf" )
print( "Done!" )

