#!/bin/tcsh

# Wrapper script to generate some spectra
# Second attempt: working from plain old event files with NO filtering
# and running on re-downloaded data, straight from XMM-Newton archive

# Run from directory: research/xmm/

# Aaron Tran
# October 25, 2015

source sasinit

# Because xmm downloaded data uses lower-case convention.
# just hardcoding it in...
setenv SAS_ODF /data/mpofls/atran/research/xmm/0087940201_redl/odf/repro/0315_0087940201_SCX00000SUM.SAS
setenv SAS_CCF /data/mpofls/atran/research/xmm/0087940201_redl/odf/repro/ccf.cif

cd 0087940201_redl/odf/repro/

evselect table=P0087940201M1S001MIEVLI0000.FIT:EVENTS filtertype=expression expression='(PATTERN<=12) && (PI in [200:12000]) && #XMMEA_EM' \
	filtertype=expression withfilteredset=yes keepfilteroutput=yes \
	filteredset='mos1S001-clean-XMMEA_EM-pattern12.fits'
especget filestem='mos1src_especget_XMMEA_EM_pattern12' table='mos1S001-clean-XMMEA_EM-pattern12.fits' \
	srcexp='((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))' \
	backexp='(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))'

evselect table=P0087940201M1S001MIEVLI0000.FIT:EVENTS filtertype=expression expression='(PATTERN<=12) && (PI in [200:12000]) && #XMMEA_SM' \
	filtertype=expression withfilteredset=yes keepfilteroutput=yes \
	filteredset='mos1S001-clean-XMMEA_SM-pattern12.fits'
especget filestem='mos1src_especget_XMMEA_SM_pattern12' table='mos1S001-clean-XMMEA_SM-pattern12.fits' \
	srcexp='((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))' \
	backexp='(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))'

evselect table=P0087940201M1S001MIEVLI0000.FIT:EVENTS filtertype=expression expression='(PATTERN<=0) && (PI in [200:12000]) && (FLAG == 0)' \
	filtertype=expression withfilteredset=yes keepfilteroutput=yes \
	filteredset='mos1S001-clean-perfect.fits'
especget filestem='mos1src_especget_perfect' table='mos1S001-clean-perfect.fits' \
	srcexp='((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))' \
	backexp='(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))'

