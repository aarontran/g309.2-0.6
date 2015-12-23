#!/data/mpcrit4/bin/perl

# Short Perl script to convert DS9 circle and annulus regions
# (or, implicit unions thereof)
# to XMM-Newton detector coordinate region expressions
#
# Assumes DS9 regions in fk5 coordinates
# (ra in h/m/s, dec in d/m/s, radius in arcseconds)
# Outputs XMM regions computed using SAS task esky2det

use strict;
use warnings;

$| = 1;  # Set autoflush

my ($region_file, $calinfoset) = @ARGV;

my $arcsec2detxy = 20;  # Each unit of DETX/Y is 0.05 arcseconds.
# see documentation at http://xmm.esac.esa.int/sas/current/doc/esky2det.pdf

my @xmm_reg;

open(my $reg_fh, "<", $region_file) or die "Couldn't find $region_file";
while(<$reg_fh>) {

    if ($_ =~ /^circle\((.+),(.+),(.+)"\)/) {

	my ($ra, $dec, $radius) = ($1, $2, $3);
	$ra =~ s/([\d]+):([\d]+):([\d.]+)/$1h$2m$3s/;  # Convert colons to h/m/s
	$dec =~ s/([\d]+):([\d]+):([\d.]+)/$1d$2m$3s/;  # Convert colons to d/m/s

	my $cmd = "esky2det datastyle='user' outunit='det' withheader='no' -V 0"
	    . " ra='$ra' dec='$dec' calinfoset='$calinfoset' checkfov='no'";
	my $result = `$cmd`;
	my ($detx, $dety) = ($result =~ /([0-9.-]+)\s+([0-9.-]+)/);
	my $detr = $radius * $arcsec2detxy;

	push @xmm_reg, "((DETX,DETY) IN circle($detx,$dety,$detr))";

    } elsif ($_ =~ /^annulus\((.+),(.+),(.+)",(.+)"\)/) {

	my ($ra, $dec, $r_in, $r_out) = ($1, $2, $3, $4);
	$ra =~ s/([\d]+):([\d]+):([\d.]+)/$1h$2m$3s/;  # Convert colons to h/m/s
	$dec =~ s/([\d]+):([\d]+):([\d.]+)/$1d$2m$3s/;  # Convert colons to d/m/s

	my $cmd = "esky2det datastyle='user' outunit='det' withheader='no' -V 0"
	    . " ra='$ra' dec='$dec' calinfoset='$calinfoset' checkfov='no'";
	my $result = `$cmd`;
	my ($detx, $dety) = ($result =~ /([0-9.-]+)\s+([0-9.-]+)/);
	my $detr_in = $r_in * $arcsec2detxy;
	my $detr_out = $r_out * $arcsec2detxy;

	push @xmm_reg, "(((DETX,DETY) IN circle($detx,$dety,$detr_out))"
	    . "&&!((DETX,DETY) IN circle($detx,$dety,$detr_in)))";
	# Outermost parens enforce precedence, despite seeming redundant
	# E.g., without parens, an external caller that tries to negate this
	# expression would operate on a component circle, not the annulus
    }
}
close($reg_fh);

if (scalar(@xmm_reg) == 1) {
    print "&&$xmm_reg[0]\n";
} else {
    print "&&( " . join(" || ", @xmm_reg) . " )\n";
}

