#!/bin/tcsh

# Code snippet -- extract very soft events to compare
# epchain runs with and without epreject.
# used previously to confirm minimal impact from epreject

cd ${XMM_PATH}/0551000201/odf/repro/

evselect table="pnS003-ori.fits" filteredset="pnS003-ori_vsoft.fits" \
    expression="(PHA>=20)&&(PI>=120)&&(PI<200)"
evselect table="pnS003-oot.fits" filteredset="pnS003-oot_vsoft.fits" \
    expression="(PHA>=20)&&(PI>=120)&&(PI<200)"
evselect table="pnS003-ori_vsoft.fits" withimageset=true \
    imageset="pnS003-ori_vsoft-img.fits" xcolumn=DETX ycolumn=DETY \
    imagebinning=binSize ximagebinsize=100 yimagebinsize=100
evselect table="pnS003-oot_vsoft.fits" withimageset=true \
    imageset="pnS003-oot_vsoft-img.fits" xcolumn=DETX ycolumn=DETY \
    imagebinning=binSize ximagebinsize=100 yimagebinsize=100
