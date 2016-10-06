#!/usr/local/bin/perl

# Pipeline script to merge multiple XMM exposures together, after successful
# run of task "specbackgrp" (which calls modified version of ESAS mos-spectra
# and pn-spectra tasks).
# Designed for use with MOS1 and MOS2 exposures specifically.
#
# MUST be run in an FTOOLS environment with $SAS_REPRO environment var set
#
# Input: region-stem (for filenames), list of XMM exposures to use
# Result: output loads of merged spectrum file in your SAS_REPRO directory.
#   (warning, ALL commands clobber files)
#
# Example:
#
#     merge_exps.pl ann_000_100 mos1S001 mos2S002
#
# This identifies all appropriately named spectrum files in $SAS_REPRO and
# dumps a slew of outputs to "mosmerge-*" in the same directory.
# Read the script to see what files are merged.
#

use 5.010;  # get 'say'
use strict;
use warnings;
use List::Util qw( sum );
$| = 1;  # Set autoflush

my $MERGEXP = "mosmerge";  # Default stem for outputs

my $RSTEM = shift;
my @EXPS = @ARGV;  # All remaining arguments

if (not $ENV{'SAS_REPRO'}) {
    die "ERROR: SAS_REPRO not set";
}
chdir($ENV{'SAS_REPRO'});

announce("Create temporary spectra to satisfy mathpha");
for my $exp (@EXPS) {
    run_and_say("cp ${exp}-${RSTEM}.pi     ${exp}_${RSTEM}.pi");   # outputs -> @obj_pha
    run_and_say("cp ${exp}-${RSTEM}-qpb.pi ${exp}_${RSTEM}_qpb.pi");  # outputs -> @obj_qpb
    run_and_say("cp ${exp}-${RSTEM}-ff.pi  ${exp}_${RSTEM}_ff.pi");  # outputs -> @fwc_pha
}

# Expected filenames, with mathpha-compatible temporary copies

my @obj_pha = map { "${_}_${RSTEM}.pi" } @EXPS;  # Note underscores
my @obj_qpb = map { "${_}_${RSTEM}_qpb.pi" } @EXPS;  # Note underscores
my @obj_rmf = map { "${_}-${RSTEM}.rmf" } @EXPS;
my @obj_arf = map { "${_}-${RSTEM}.arf" } @EXPS;
my @obj_flatrmf = map { "${_}-${RSTEM}.flatrmf" } @EXPS;
my @obj_flatarf = map { "${_}-${RSTEM}.flatarf" } @EXPS;

my @fwc_pha = map { "${_}_${RSTEM}_ff.pi" } @EXPS;  # Note underscores
my @fwc_rmf = map { "${_}-${RSTEM}-ff.rmf" } @EXPS;
my @fwc_arf = map { "${_}-${RSTEM}-ff.arf" } @EXPS;

my @obj_weights = exposure_weights(@obj_pha);
my @fwc_weights = exposure_weights(@fwc_pha);


announce("Merging observation pha, qpb, rmf, arf files");
merge_pha(\@obj_pha,		    "${MERGEXP}-${RSTEM}.pi");
merge_pha(\@obj_qpb,		    "${MERGEXP}-${RSTEM}-qpb.pi");
merge_rmf(\@obj_rmf, \@obj_weights, "${MERGEXP}-${RSTEM}.rmf");
merge_arf(\@obj_arf, \@obj_weights, "${MERGEXP}-${RSTEM}.arf");

merge_rmf(\@obj_flatrmf, \@obj_weights, "${MERGEXP}-${RSTEM}.flatrmf");
merge_rmf(\@obj_flatarf, \@obj_weights, "${MERGEXP}-${RSTEM}.flatarf");

announce("Merging FWC pha, rmf, arf files");
merge_pha(\@fwc_pha,		    "${MERGEXP}-${RSTEM}-ff.pi");
merge_rmf(\@fwc_rmf, \@fwc_weights, "${MERGEXP}-${RSTEM}-ff.rmf");
merge_arf(\@fwc_arf, \@fwc_weights, "${MERGEXP}-${RSTEM}-ff.arf");

# Special cases -- sum FWC RMF, ARF using observation exposure time weights
# instead of FWC weights (expect marginal difference).
# To be used for fitting instrumental lines in merged observation data.
# (for unmerged data, just use -ff.rmf/-ff.arf)
announce("Merging FWC rmf, arf files with obs exposure weighting");
merge_rmf(\@fwc_rmf, \@obj_weights, "${MERGEXP}-${RSTEM}-ff-instr.rmf");
merge_arf(\@fwc_arf, \@obj_weights, "${MERGEXP}-${RSTEM}-ff-instr.arf");

# Same as above, but now use multiplied RMF/ARF files instead
# (more rigorously correct weighting)
announce("Multiplying observation & FWC rmf,arf files");
my @obj_marfrmf = map { "${_}-${RSTEM}.marfrmf" } @EXPS;;
my @fwc_marfrmf = map { "${_}-${RSTEM}-ff.marfrmf" } @EXPS;;
my @obj_flatmarfrmf = map { "${_}-${RSTEM}.flatmarfrmf" } @EXPS;;
for my $i (0..$#obj_pha) {
    marfrmf($obj_rmf[$i], $obj_arf[$i], $obj_marfrmf[$i]);
    marfrmf($fwc_rmf[$i], $fwc_arf[$i], $fwc_marfrmf[$i]);
    marfrmf($obj_flatrmf[$i], $obj_flatarf[$i], $obj_flatmarfrmf[$i]);
}
announce("Merging multiplied rmf,arf files (correct merger weighting)");
merge_rmf(\@obj_marfrmf, \@obj_weights, "${MERGEXP}-${RSTEM}.marfrmf");
merge_rmf(\@fwc_marfrmf, \@fwc_weights, "${MERGEXP}-${RSTEM}-ff.marfrmf");
merge_rmf(\@fwc_marfrmf, \@obj_weights, "${MERGEXP}-${RSTEM}-ff-instr.marfrmf");
merge_rmf(\@obj_flatmarfrmf, \@obj_weights, "${MERGEXP}-${RSTEM}.flatmarfrmf");

announce("Apply standard keywording (use .marfrmf files)");
run_and_say("grppha infile=\"${MERGEXP}-${RSTEM}.pi\""
	    . " outfile=\"!${MERGEXP}-${RSTEM}.pi\""
	    . " comm=\"chkey BACKFILE ${MERGEXP}-${RSTEM}-qpb.pi &"
	    . " chkey RESPFILE ${MERGEXP}-${RSTEM}.marfrmf &"
	    . " chkey ANCRFILE NONE &"
            . " exit\"");
run_and_say("grppha infile=\"${MERGEXP}-${RSTEM}-ff.pi\""
	    . " outfile=\"!${MERGEXP}-${RSTEM}-ff.pi\""
	    . " comm=\"chkey BACKFILE NONE &"
	    . " chkey RESPFILE ${MERGEXP}-${RSTEM}-ff.marfrmf &"
	    . " chkey ANCRFILE NONE &"
            . " exit\"");

announce("Group merged spectra");
run_and_say("grppha infile=\"${MERGEXP}-${RSTEM}.pi\""
	    . " outfile=\"!${MERGEXP}-${RSTEM}-grp01.pi\""
	    . " comm=\"group min 1 & exit\"");
run_and_say("grppha infile=\"${MERGEXP}-${RSTEM}.pi\""
	    . " outfile=\"!${MERGEXP}-${RSTEM}-grp50.pi\""
	    . " comm=\"group min 50 & exit\"");

announce("Remove temporary spectra & exposure-specific multiplied RMF/ARF files");
for my $exp (@EXPS) {
    run_and_say("rm ${exp}_${RSTEM}.pi");  # equivalent to @obj_pha
    run_and_say("rm ${exp}_${RSTEM}_qpb.pi");  # equivalent to @obj_qpb
    run_and_say("rm ${exp}_${RSTEM}_ff.pi");  # equivalent to @fwc_pha
    # These are needed to create merged .marfrmf files, but alone are
    # equivalent to loading RMF/ARF files separately, so are not needed
    run_and_say("rm ${exp}-${RSTEM}.marfrmf");  # equivalent to @obj_marfrmf
    run_and_say("rm ${exp}-${RSTEM}-ff.marfrmf");  # equivalent to @fwc_marfrmf
    run_and_say("rm ${exp}-${RSTEM}.flatmarfrmf");  # equivalent to @obj_flatmarfrmf
}

###############################################################################

# Just a perl wrapper for ftool marfrmf
# Input: RMF filename, ARF filename, output filename
# Output: n/a, commands executed
sub marfrmf {
    my ($rmf, $arf, $out) = @_;
    run_and_say("marfrmf $rmf $arf \"!$out\"");
}

# Input: reference to list of PHA names, output filename
# Output: n/a, commands executed
sub merge_pha {

    my @phas = @{$_[0]};
    my $f_out = $_[1];

    my $expr = join(" + ", @phas);
    my $backscal = eff_backscal(@phas);
    my $comm = <<EOF;
mathpha expr="${expr}" outfil="!${f_out}" \\
    units=C exposure=CALC backscal='$backscal' areascal='%' ncomments=0
EOF
    run_and_say($comm);
}

# Input: array-ref to list of RMF names, array-ref to weights, output filename
# Output: n/a, commands executed
sub merge_rmf {

    my @rmfs = @{$_[0]};
    my @weights = @{$_[1]};
    my $f_out = $_[2];

    my $rmfs = join(" ", @rmfs);
    my $weights = join(" ", @weights);
    run_and_say("addrmf \"$rmfs\" \"$weights\" \"!$f_out\"");
}

# Input: array-ref to list of ARF names, array-ref to weights, output filename
# Output: n/a, commands executed
sub merge_arf {

    my @arfs = @{$_[0]};
    my @weights = @{$_[1]};
    my $f_out = $_[2];

    my $arfs = join(" ", @arfs);
    my $weights = join(" ", @weights);
    run_and_say("addarf \"$arfs\" \"$weights\" \"!$f_out\"");
}

###############################################################################

# Kind of ridiculous but OK
sub announce {
    say "========== $_[0] ==========";
}

# Input: 0 or more FITS filenames
# Output: exposure weighted effective BACKSCAL
sub eff_backscal {
    my @phas = @_;
    my $backscal_eff = 0;
    my @backscals = map { kw("BACKSCAL", $_) } @phas;
    my @weights = exposure_weights(@phas);
    for my $i (0..$#backscals) {
	# += BACKSCAL_i * t_i / (sum_j t_j)
	$backscal_eff += $backscals[$i] * $weights[$i];
    }
    return $backscal_eff;
}

# Input: 0 or more FITS filenames
# Output: list of exposure weights (sum to 1)
sub exposure_weights {
    my @phas = @_;
    my @exposures = map { kw("EXPOSURE", $_) } @phas;
    my $total = sum(@exposures);
    my @weights = map { sprintf("%.6f", $_ / $total) } @exposures;
    return @weights;
}

# Input: keyword, FITS filename (only works for numerical keywords: EXPOSURE,
# BACKSCAL, etc...)
# Output: value assigned to keyword
sub kw {
    my ($kw, $fname) = @_;
    # `fkeyprint ... | grep ... | awk ...` taken from Fin_over_Fout
    my $entry = `fkeyprint \"${fname}\[1\]\" $kw | grep =`;
    die "ERROR: $fname has no keyword $kw" if not $entry;
    my $val = (split(/\s+/, $entry))[1];
    return $val;
}

# Input: command (string) to pass to shell
# Output: n/a, command run and printed
sub run_and_say {
    my $comm = shift;
    say "$comm";
    system "$comm";
}
