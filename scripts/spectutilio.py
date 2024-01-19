from pyteomics import mzml, mgf, mzxml
import spectrum_utils.plot as sup
import spectrum_utils.spectrum as sus
import matplotlib.pyplot as plt
import re

min_peaks = 10
min_mz, max_mz = 100, 1500
fragment_tol_mass, fragment_tol_mode = 0.02, "Da"
min_intensity = 0.02
max_num_peaks = 200

def get_spectrum_from_mgf( mgf_file, target_scan_id ):
    for spec_dict in mgf.read(mgf_file):
        # Omit invalid spectra.
        if len(spec_dict["m/z array"]) < min_peaks: continue
        if "charge" not in spec_dict["params"]: continue

        scan = int( re.split('=|:', spec_dict["params"]["title"])[-1] )
        if scan == target_scan_id:
            spectrum = sus.MsmsSpectrum(
              spec_dict["params"]["title"],
              spec_dict["params"]["pepmass"][0],
              spec_dict["params"]["charge"][0],
              spec_dict["m/z array"],
              spec_dict["intensity array"],
              float(spec_dict["params"]["rtinseconds"]),
            )
            spectrum.set_mz_range(min_mz, max_mz)
            spectrum.remove_precursor_peak(fragment_tol_mass, fragment_tol_mode)
            spectrum.filter_intensity(min_intensity, max_num_peaks)
            spectrum.scale_intensity("root", 1)
            return spectrum
    print("Not found!")
    return None

def get_spectrum_from_mzML( mzml_file, target_scan_id ):
    for spec_dict in mzml.read(mzml_file):
        # Omit invalid spectra.
        if len(spec_dict["m/z array"]) < min_peaks: continue

        ndx = int(spec_dict['id'].split()[-1].split('=')[-1])
        if ndx == target_scan_id:
          spectrum = sus.MsmsSpectrum(
            spec_dict["id"],
            spec_dict["base peak m/z"],
            spec_dict["total ion current"],
            spec_dict["m/z array"],
            spec_dict["intensity array"],
            float(spec_dict['scanList']['scan'][0]['scan start time']),
          )
          spectrum.set_mz_range(min_mz, max_mz)
          spectrum.remove_precursor_peak(fragment_tol_mass, fragment_tol_mode)
          spectrum.filter_intensity(min_intensity, max_num_peaks)
          spectrum.scale_intensity("root", 1)
          return spectrum
    print("Not found!")
    return None

def get_spectrum_from_mzXML( mzxml_file, target_scan_id ):
    for spec_dict in mzxml.read(mzxml_file):
        # Omit invalid spectra.
        if len(spec_dict["m/z array"]) < min_peaks: continue

        ndx = int(spec_dict['id'].split()[-1].split('=')[-1])
        if ndx == target_scan_id:
            spectrum = sus.MsmsSpectrum(
              spec_dict["id"],
              spec_dict["basePeakMz"],
              spec_dict["totIonCurrent"],
              spec_dict["m/z array"],
              spec_dict["intensity array"],
              float(spec_dict['retentionTime']),
            )
            spectrum.set_mz_range(min_mz, max_mz)
            spectrum.remove_precursor_peak(fragment_tol_mass, fragment_tol_mode)
            spectrum.filter_intensity(min_intensity, max_num_peaks)
            spectrum.scale_intensity("root", 1)
            return spectrum
    print("Not found!")
    return None

def draw_spect_pep_pdf( spectrum, peptide_str, out_fn ):
    # Annotate the spectrum with its ProForma string.
    spectrum = spectrum.annotate_proforma(peptide_str, 0.5, "Da", ion_types="abyIm")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title(peptide_str, fontdict={"fontsize": "xx-large"})

    draw_spect_pdf( spectrum, out_fn, ax )
    plt.close()
    
def draw_spect_pdf( spectrum, out_fn, ax ):
    # Plot the spectrum.
    sup.spectrum(spectrum, grid=False, ax=ax)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    plt.savefig(out_fn, bbox_inches="tight", dpi=300, transparent=False)

