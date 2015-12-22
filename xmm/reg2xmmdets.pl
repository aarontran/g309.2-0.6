#!/data/mpcrit4/bin/perl

# Short Perl script to convert DS9 circle regions
# (or, implicit unions of circles)
# to XMM-Newton detector coordinate region expressions
# for spectrum extraction etc.
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

    next if $_ !~ /^circle/;

    my ($ra,$dec,$radius) = /^circle\((.+),(.+),(.+)"\)/;
    $ra =~ s/([\d]+):([\d]+):([\d.]+)/$1h$2m$3s/;  # Convert colons to h/m/s
    $dec =~ s/([\d]+):([\d]+):([\d.]+)/$1d$2m$3s/;  # Convert colons to d/m/s

    my $cmd = "esky2det datastyle='user' outunit='det' withheader='no' -V 0"
        . " ra='$ra' dec='$dec' calinfoset='$calinfoset' checkfov='no'";
    my $result = `$cmd`;
    my ($detx, $dety) = ($result =~ /([0-9.-]+)\s+([0-9.-]+)/);
    my $detr = $radius * $arcsec2detxy;

    push @xmm_reg, "((DETX,DETY) IN circle($detx, $dety, $detr))";
}
close($reg_fh);

if (scalar(@xmm_reg) == 1) {
    print "&&$xmm_reg[0]\n";
} else {
    print "&&( " . join(" || ", @xmm_reg) . " )\n";
}

