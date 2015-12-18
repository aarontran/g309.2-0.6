"""
chains and filtering, python implementation...
"""

import argparse
import os
from subprocess import call


DAT = {'0087940201':
            {'exps': ["mos1S001", "mos2S002", "pnS003"],
             'gtis': ["(TIME >= 115364540)",
                      "(TIME >= 115364540)",
                      "(TIME >= 115364540)"],
             'epreject': False
            },
       '0551000201':
            {'exps': ["mos1S001", "mos2S002", "pnS003"],
             'gtis': ["!(TIME IN [352743736:352756237])",
                      "!(TIME IN [352743736:352756237])",
                      "(TIME < 352755947)"],
             'epreject': True
            }
      }

# ------------------------
# Start of script commands
# ------------------------

def sh(cmd):
    """Wrapper for subprocess.call, to run commands through shell"""
    #return call(cmd, shell=True)
    return 0

def pn(str):
    return str[:2].lower() == "pn"

def mos(str):
    return str[:3].lower() == "mos"

def main():

    parser = argparse.ArgumentParser(description="Chainfilter")
    parser.add_argument('obsid', help="XMM obsid to reduce and filter")
    opt = parser.parse_args()

    obsid = opt.obsid
    if obsid not in DAT:
        raise ValueError("Invalid obsid {0} provided".format(obsid))

    os.chdir("{0}/{1}/odf/repro".format(os.environ['XMM_PATH'], obsid))

    # This works!
    # call(["evselect table=mos1S001-clean.fits filteredset=asdffilt.fits expression='#XMMEA_EM'", shell=True)
    # This does not!
    # call(["evselect", "table=mos1S001-clean.fits", "filteredset=asdffilt.fits", "expression='#XMMEA_EM'"])

    # Generate event lists
    sh("emchain >& emchain.log")
    if DAT[obsid]['epreject']:
        sh("epchain withoutoftime=true runepreject=Y sigma=5 >& epchain_oot.log"
        sh("epchain runepreject=Y sigma=5 >& epchain.log")
    else:
        sh("epchain withoutoftime=true >& epchain_oot.log")
        sh("epchain >& epchain.log")

    # Good time filtering (remove flares)
    sh("mos-filter >& mos-filter.log")
    sh("mv command.csh mos-filter_cmd.csh")
    sh("pn-filter >& pn-filter.log")

    for exp, gtifilt in zip(DAT[obsid]['exps'], DAT[obsid]['gtis']:

        # Move -gti.{fits,txt} in case any ESAS tasks surreptitiously use these
        # files, as they're not valid after our manual GTI editing
        sh("mv {0}-clean.fits {0}-clean-ori.fits".format(exp))
        sh("mv {0}-gti.fits   {0}-gti-ori.fits".format(exp))
        sh("mv {0}-gti.txt    {0}-gti-ori.txt".format(exp))
        if pn(exp):
            sh("mv {0}-clean-oot.fits {0}-clean-oot-ori.fits".format(exp))
            sh("mv {0}-gti-oot.fits   {0}-gti-oot-ori.fits".format(exp))
            sh("mv {0}-gti-oot.txt    {0}-gti-oot-ori.txt".format(exp))

        # Cut events in first ~10ks of observation (0087940201 MOS and PN)
        sh("evselect table={0}-clean-ori.fits".format(exp)
           + " filteredset={0}-clean2.fits".format(exp)
           + " expression='{0}'".format(gtifilt)
           + " updateexposure=yes filterexposure=yes"
           + " keepfilteroutput=yes withfilteredset=yes filtertype=expression")

        # Light curves to check that manual time cuts were applied successfully
        # Match filtering params for ${exp}-rate.fits from espfilt
        pattfilt = "(PATTERN<=12)"
        if pn(exp):
            pattfilt = "(PATTERN<=4)"

        # ${exp}-ori-lc.fits is the same as ${exp}-rate.fits, but with coarser binning
        sh("evselect table={0}-ori.fits rateset={0}-ori-lc.fits".format(exp) +
           " expression='{0}&&(PI in [2500:12000])".format(pattfilt) +
               "&&((FLAG & 0xfb0000)==0)&&((FLAG & 0x766a0f63)==0)'" +
           " withrateset=yes maketimecolumn=yes makeratecolumn=yes" +
           " timecolumn='TIME' timebinsize=50 keepfilteroutput=no")

        sh("evselect table={0}-clean-ori.fits rateset={0}-clean-ori-lc.fits".format(exp) +
           " expression='(PI in [2500:12000])&&((FLAG & 0xfb0000) == 0)'" +
           " withrateset=yes maketimecolumn=yes makeratecolumn=yes" +
           " timecolumn='TIME' timebinsize=50 keepfilteroutput=no")

        sh("evselect table={0}-clean2.fits rateset={0}-clean-final-lc.fits".format(exp) +
           " expression='(PI in [2500:12000])&&((FLAG & 0xfb0000) == 0)'" +
           " withrateset=yes maketimecolumn=yes makeratecolumn=yes" +
           " timecolumn='TIME' timebinsize=50 keepfilteroutput=no")

        # 0x766a0f63 is used for obsids before XMM revolution 2383 in espfilt and {mos,pn}-filter
        # 0xfb0000 is used in espfilt to create FOV lightcurves; this removes out
        # of FOV events and obviously bad events (cosmic rays, bad pixels, etc)

        # Final manual filtering
        # mos{1S001,2S002}-clean-ori.fits were already filtered by:
        #  '(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)'
        # pnS003-clean-ori.fits was already filtered by:
        #  '(PATTERN<= 4)&&((FLAG & 0x766a0f63)==0)'
        # Nevertheless re-specify PATTERN to be quite explicit.
        # Note that FLAG filtering may be overly restrictive for images
        finalfilt = "(PATTERN<=12)&&#XMMEA_EM"
        if pn(exp):
            finalfilt = "(PATTERN<=4)&&(FLAG==0)"

        sh("evselect table={0}-clean2.fits filteredset={0}-clean.fits".format(exp) +
           " expression='{0}'".format(finalfilt) +
           " updateexposure=no filterexposure=no" +
           " keepfilteroutput=yes withfilteredset=yes filtertype=expression")


    # cheese must be run after manual GTI edits; probably benefits from running
    # after additional FLAG filter step
    sh("cheese prefixm='{MOSEXP_N}' prefixp='${PNEXP_N}'" +
       " scale=0.5 rate=2.0 dist=40.0 clobber=1 elow=400 ehigh=7200")
    sh("mv command.csh cheese_cmd.csh")
    sh("mv emllist.fits cheese_emllist.fits")


# TODO currently unused
def bin_lc(table="", rateset="", expression="", binsize=50):
    """Generate lightcurve with a few pre-set parameters"""
    return sh("evselect table={0} rateset={1}".format(table, rateset) +
              " expression='{0}'".format(expression) +
              " withrateset=yes maketimecolumn=yes makeratecolumn=yes" +
              " timecolumn='TIME' timebinsize={0}".format(binsize) +
              " keepfilteroutput=no")

if __name__ == '__main__':
    main()

