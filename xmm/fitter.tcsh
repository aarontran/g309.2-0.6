#!/usr/bin/env tcsh

# this is fiendishly ugly -- want to do this in ipython notebook instead...
# the first few lines of every invocation are PUUUURE boilerplate

# Useful to pipe this to a log file, or monitor output

# MUST BE RUN FROM XMM_PATH CURRENTLY (hard coded)

# Need tcsh to run `source sasinit`
# Need this for PyXSPEC
source sasinit

#echo "========== Fit: background region, XRB alone =========="
#
#ipython --c 'from IPython import get_ipython; ipy = get_ipython(); \
#ipy.magic("%run xspec_fit_g309.py bkg --snr_model=xrb") ; \
#dump_plots_data("bkg_test")'

#echo "========== Fit: src+bkg region, stepping XRB nH =========="
#
## This is obviously very slow (!) takes a while to step over nH
#ipython --c 'from IPython import get_ipython; ipy = get_ipython(); \
#ipy.magic("%run xspec_fit_g309.py src --snr_model=vnei --with_bkg") ; \
#xs.Fit.steppar("xrb:6 0.1 4.0 40")
#dump_plots_data("bkg_nH_test")'

# This could be easily parallelized... TBD.

# TRIAL RUN looked ok so proceed
#set regions = "ann_000_100 src_north_clump"

# skip src_pre_ridge, not too useful presently

set regions = "src_E_lobe src_SW_lobe src_SE_dark \
src_ridge src_SE_ridge_dark \
ann_100_200 ann_200_300 ann_300_400 ann_400_500"

#set regions = "src_north_clump src_E_lobe src_SW_lobe src_SE_dark \
#src_ridge src_SE_ridge_dark src_pre_ridge \
#ann_000_100 ann_100_200 ann_200_300 ann_300_400 ann_400_500"

set nH_vals = "1.5 2.0 2.5 3.0"

foreach reg ($regions)

  echo "========== Fit: ${reg}, default XRB, free nH =========="

  # PLEASE NOTE: this script will die / stall horrifically if the output qdp
  # file already exists...  Here's a hacky workaround.
  rm -f "results_spec/${reg}.qdp"

  # Default nH free fit!
  ipython --c "from IPython import get_ipython; ipy = get_ipython(); \
ipy.magic('%run xspec_fit_g309.py ${reg} --snr_model=vnei'); \
dump_plots_data('results_spec/${reg}');"

end


foreach nH ($nH_vals)

  echo "========== Fit: ${reg}, default XRB, varying nH =========="

  foreach reg ($regions)

    echo "---------- Fit: ${reg}, default XRB, nH = ${nH} ----------"
  
    rm -f "results_spec/${reg}_nH-${nH}.qdp"
  
    ipython --c "from IPython import get_ipython; ipy = get_ipython(); \
ipy.magic('%run xspec_fit_g309.py ${reg} --snr_model=vnei --n_H=${nH}'); \
dump_plots_data('results_spec/${reg}_nH-${nH}');"

  end

end

