# Top-level Make for this project
#
# Must run from top-level directory: /data/mpofls/atran/research/g309/xmm/
#
# Assumes directory structure:
#   ./$obsid
#   ./$obsid/odf
#   ./$obsid/odf/repro
#   ./$obsid/pps
# and, for esas caldb files:
#   ./caldb/*.rsp
#
# Expected output: ccf.cif and *SUM.SAS files for all XMM obsids specified
# and a clean ESAS CALDB download, with mos1/mos2/pn diagonal RMFs extracted
# and placed in a "standard" location.

OBSIDS = 0087940201 0551000201

CCF = %/odf/repro/ccf.cif

# need tcsh to source sasinit/sasrepro; fails in bash/sh
SHELL = /bin/tcsh
SASINIT = source /data/mpofls/atran/research/g309/xmm/sasinit
SASREPRO = source /data/mpofls/atran/research/g309/xmm/sasrepro


.PHONY : all
all : $(patsubst %, $(CCF), $(OBSIDS)) caldb

# ODF summary %/odf/repro/$(REV)_%_SCX00000SUM.SAS is also created by
# $(SASREPRO), but it's not targeted because its name is hard to specify.
# If ccf.cif is up-to-date, *SUM.SAS will also be up-to-date.
# Makefiles within %/odf/repro will check for both ccf.cif and *SUM.SAS
# and both can be regenerated with this top-level Makefile.
$(CCF) : files_%.tar
	tar -xf $<
	tar -xzf $*/odf/$*.tar.gz --directory=$*/odf
	tar -xf $*/odf/*_$*.TAR --directory=$*/odf
	$(SASINIT) ; $(SASREPRO) $*

files_%.tar :
	curl -o $@ \
	  "http://nxsa.esac.esa.int/nxsa-sl/servlet/data-action-aio?obsno=$*"


.PHONY : caldb
caldb : caldb/mos1-diag.rsp caldb/mos2-diag.rsp caldb/pn-diag.rsp

# Note: I'd expect "make CALDB ; make CALDB" to execute twice, because the
# immediate dependencies caldb/%.rsp.gz are removed by gunzip.
# But, apparently make is smart enough to bypass this.
# Make also 'rm's the gzipped files (even though not instructed to do so)
caldb/%.rsp : caldb/%.rsp.gz
	gunzip -c $< > $@

caldb/%.rsp.gz : esas-caldb-sasv13.tar.gz
	mkdir -p caldb
	tar -xzvf $< --directory caldb
	touch caldb/*

esas-caldb-sasv13.tar.gz :
	curl --verbose --user anonymous:-curl@ -o $@ \
	  "ftp://xmm.esac.esa.int/pub/ccf/constituents/extras/esas_caldb/esas-caldb-sasv13.tar.gz"
# Password "-curl@" mimicks wget behavior; curl's default password
# "ftp@example.com" is rejected by XMM SOC ftp.
