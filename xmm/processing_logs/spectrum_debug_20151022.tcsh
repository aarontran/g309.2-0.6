#!/bin/tcsh

# Wrapper script to generate some spectra
# assumes that mos-filter has already been run
# tailor made for a specific OBSID (0087940201)

# Run from directory: research/xmm/
# script will CD as needed.

# Aaron Tran
# October 22, 2015

source sasinit
source sas_setpaths 0087940201_esas

cd 0087940201_esas/ODF/repro/

evselect table=mos1S001-clean.fits:EVENTS filtertype=expression expression='(PATTERN<=12) && (PI in [200:12000]) && #XMMEA_EM' \
	filtertype=expression withfilteredset=yes keepfilteroutput=yes \
	filteredset='mos1S001-clean-XMMEA_EM-pattern12.fits'
especget filestem='mos1src_especget_XMMEA_EM_pattern12' table='mos1S001-clean-XMMEA_EM-pattern12.fits' \
	srcexp='((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))' \
	backexp='(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))'

evselect table=mos1S001-clean.fits:EVENTS filtertype=expression expression='(PATTERN<=12) && (PI in [200:12000]) && #XMMEA_SM' \
	filtertype=expression withfilteredset=yes keepfilteroutput=yes \
	filteredset='mos1S001-clean-XMMEA_SM-pattern12.fits'
especget filestem='mos1src_especget_XMMEA_SM_pattern12' table='mos1S001-clean-XMMEA_SM-pattern12.fits' \
	srcexp='((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))' \
	backexp='(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))'

evselect table=mos1S001-clean.fits:EVENTS filtertype=expression expression='(PATTERN<=0) && (PI in [200:12000]) && (FLAG == 0)' \
	filtertype=expression withfilteredset=yes keepfilteroutput=yes \
	filteredset='mos1S001-clean-perfect.fits'
especget filestem='mos1src_especget_perfect' table='mos1S001-clean-perfect.fits' \
	srcexp='((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))' \
	backexp='(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))'

