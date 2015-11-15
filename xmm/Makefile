
# WARNING: following directory structure required
#   ./$obsid
#   ./$obsid/odf
#   ./$obsid/odf/repro
#   ./$obsid/pps
#
#   ./caldb/*.rsp
#
# Basically, you must run this from the top-level directory
# /data/mpofls/atran/research/g309/xmm/



OBSID = 0087940201
REV = 0315
#OBSID = 0551000201
#REV = 1692

# Paths
include config.mk
ODF = $(OBSID)/odf  # Set by downloaded tar structure
REPRO = $(OBSID)/odf/repro  # Directory structure fixed here and in sasrepro

# Scripts/tools
SASINIT = /data/mpofls/atran/research/g309/xmm/sasinit
SASREPRO = /data/mpofls/atran/research/g309/xmm/sasrepro

# Variables, targets, etc
CCF = $(REPRO)/ccf.cif
SOSF = $(REPRO)/$(REV)_$(OBSID)_SCX00000SUM.SAS

# -----------------------
# Start of Makefile rules
# -----------------------


.PHONY : repro
repro : 0087940201/odf/repro/ccf.cif
#	0087940201/odf/repro/0315_0087940201_SCX00000SUM.SAS
#	0551000201/odf/repro/ccf.cif \
#	0551000201/odf/repro/1692_0551000201_SCX00000SUM.SAS

# QUESTION: does this work, with * for the revolution number?
# Answer: in "static pattern rules" (4.12.1), wildcard * does NOT work in the
# target pattern string.
# Answer 2: in "pattern rules" (10.5.1), wildcard * does NOT work in the target
# string.  make fails to match "blah_0087940201.SAS" to "*_%.SAS"
# HOW DO I DEAL WITH THIS CASE?

#%/repro/ccf.cif %/repro/*_SCX00000SUM.SAS : files_%.tar
#	tar -xf $<
#	tar -xzf $*/$*.tar.gz --directory=$*/odf
#	tar -xf $*/odf/*_$*.TAR --directory=$*/odf
#	mkdir -p $@
#	$(SASREPRO) $*

# Alternate?  Problem: need to parse out obsid from target
# to determine correct recipe... feed through sed or something. yuck.
# use ODF summary file to signal successful extraction and parse
# $(revolution)_$(obsid) for us
#%_SCX00000SUM.ASC :
#	tar -xf $<
#	tar -xzf $*/$*.tar.gz --directory=$*/odf
#	tar -xf $*/odf/*_$*.TAR --directory=$*/odf

# Hack.  Only works for specific two obsids under consideration
# Hack.  Requires source invocation
SHELL = /bin/tcsh  # TODO I don't like this at all.

# TODO
# I want to express the dependency on the odfingest *_*_SUM.SAS file
# but it seems absurdly convoluted to do so?!
%/odf/repro/ccf.cif : files_%.tar
	tar -xf $<
	tar -xzf $*/odf/$*.tar.gz --directory=$*/odf
	tar -xf $*/odf/*_$*.TAR --directory=$*/odf
	source $(SASINIT) ; source $(SASREPRO) $*
#	source $(SASINIT) ; $(SASREPRO) $*
#	THIS DOES NOT WORK, and I do NOT understand why.

# NOT OK because I cannot repeat % twice in a target
#%/odf/repro/ccf.cif %/odf/repro/0315_%_SCX00000SUM.SAS : %/odf/0315_%_SCX00000SUM.ASC
#	tar -xf $<
#	tar -xzf $*/odf/$*.tar.gz --directory=$*/odf
#	tar -xf $*/odf/*_$*.TAR --directory=$*/odf
#	source $(SASINIT) ; $(SASREPRO) $*
#%/odf/1692_%_SCX00000SUM.ASC : files_%.tar
#	tar -xf $<
#	tar -xzf $*/odf/$*.tar.gz --directory=$*/odf
#	tar -xf $*/odf/*_$*.TAR --directory=$*/odf
#	touch $@
#
#%/odf/0315_%_SCX00000SUM.ASC : files_%.tar
#	tar -xf $<
#	tar -xzf $*/odf/$*.tar.gz --directory=$*/odf
#	tar -xf $*/odf/*_$*.TAR --directory=$*/odf
#	touch $@

files_%.tar :
	curl -o $@ "http://nxsa.esac.esa.int/nxsa-sl/servlet/data-action-aio?obsno=$*"

# -----
# CALDB
# -----

.PHONY : caldb
caldb : caldb/mos1-diag.rsp caldb/mos2-diag.rsp caldb/pn-diag.rsp

# Note: one would expect "make CALDB ; make CALDB" to execute twice,
# because the immediate dependencies caldb/%.rsp.gz are removed by gunzip.
# But, apparently make is smart enough to bypass this, and make also 'rm's the
# gzipped files (even though not instructed to do so)
caldb/%.rsp : caldb/%.rsp.gz
	gunzip -c $< > $@

caldb/%.rsp.gz : esas-caldb-sasv13.tar.gz
	mkdir -p caldb
	tar -xzvf $< --directory caldb
	touch caldb/*

esas-caldb-sasv13.tar.gz :
	curl -o $@ "ftp://xmm.esac.esa.int/pub/ccf/constituents/extras/esas_caldb/esas-caldb-sasv13.tar.gz" \
	    --verbose --user anonymous:-curl@
# Password "-curl@" mimicks wget behavior; curl's default password
# "ftp@example.com" is rejected by XMM SOC ftp.
