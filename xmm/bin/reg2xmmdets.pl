#!/data/mpcrit4/bin/perl

# Short Perl script to convert DS9 regions (and implicit unions thereof)
# to XMM-Newton detector coordinate region expressions
#
# Coordinate conversions computed using SAS task esky2det
#
# Reference for XMM selection regions:
# https://xmm-tools.cosmos.esa.int/external/sas/current/doc/selectlib/node15.html
#
# Input: DS9 regions in fk5 coordinates
# (ra in h/m/s, dec in d/m/s, radius in arcseconds),
# and XMM event list for a given obsid/exposure
#
# Output: XMM region expressions printed to STDOUT

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

	my ($detx, $dety) = radec2detxy($ra, $dec);
	my $detr = $radius * $arcsec2detxy;

	push @xmm_reg, "((DETX,DETY) IN circle($detx,$dety,$detr))";

    } elsif ($_ =~ /^annulus\((.+),(.+),(.+)",(.+)"\)/) {

	my ($ra, $dec, $r_in, $r_out) = ($1, $2, $3, $4);

	my ($detx, $dety) = radec2detxy($ra, $dec);
	my $detr_in = $r_in * $arcsec2detxy;
	my $detr_out = $r_out * $arcsec2detxy;

	push @xmm_reg, "(((DETX,DETY) IN circle($detx,$dety,$detr_out))"
	    . "&&!((DETX,DETY) IN circle($detx,$dety,$detr_in)))";
	# Outermost parens enforce precedence, despite seeming redundant.
	# Without parens, an external caller that tries to negate this region
	# would only negate the first component circle, not the annulus

    } elsif ($_ =~ /^box\((.+),(.+),(.+)",(.+)",(.+)\)/) {
	# DS9 box dimensions are full widths, whereas XMM uses half widths

	my ($ra, $dec, $x_width, $y_width, $angle) = ($1, $2, $3, $4, $5);

	my ($detx, $dety) = radec2detxy($ra, $dec);  # center of rectangle
	my $x_halfw_det = $x_width * $arcsec2detxy / 2;  # hw = half width
	my $y_halfw_det = $y_width * $arcsec2detxy / 2;
	my $detangle = sky2detangle($angle);

	push @xmm_reg, "((DETX,DETY) IN"
	    . " box($detx,$dety,$x_halfw_det,$y_halfw_det,$detangle))";

    } elsif ($_ =~ /^ellipse\((.+),(.+),(.+)",(.+)",(.+)\)/) {
	# DS9 ellipses specified by major/minor radii
	# so they match XMM x/y half widths

	my ($ra, $dec, $r_x, $r_y, $angle) = ($1, $2, $3, $4, $5);

	my ($detx, $dety) = radec2detxy($ra, $dec);  # center of rectangle
	my $r_x_det = $r_x * $arcsec2detxy;
	my $r_y_det = $r_y * $arcsec2detxy;
	my $detangle = sky2detangle($angle);

	push @xmm_reg, "((DETX,DETY) IN"
	    . " ellipse($detx,$dety,$r_x_det,$r_y_det,$detangle))";

    } elsif ($_ =~ /^panda\((.+),(.+),(.+),(.+),([0-9]+),(.+)",(.+)",([0-9]+)\)/) {
	# NOTE: only handles "panda" regions with single sector
	# (one pair of annuli, angles)

	my ($ra, $dec, $angle_0, $angle_1, $n_angle, $r_in, $r_out, $n_annulus)
	    = ($1, $2, $3, $4, $5, $6, $7, $8);

	unless ($n_angle == 1 && $n_annulus == 1) {
	    die "ERROR: invalid panda region: $_";
	}

	my ($detx, $dety) = radec2detxy($ra, $dec);  # panda center

	# Return numbers in detector pixels to only %.1f precision
	# given that pixels are so small.

	# NOTE: due to sky <-> DETX/Y angle conversion, orientation also swaps

	my $sector = sprintf("sector(%.1f,%.1f,%.6f,%.6f)", $detx, $dety,
			sky2detangle($angle_1), sky2detangle($angle_0));
	# is "annulus" a new selection region?
	my $annulus = sprintf("annulus(%.1f,%.1f,%.1f,%.1f)", $detx, $dety,
			$r_in * $arcsec2detxy, $r_out * $arcsec2detxy);

	# Enclosing angular sector (no radius cut)
	push @xmm_reg, "(((DETX,DETY) IN $sector)&&((DETX,DETY) IN $annulus))";

    }

}
close($reg_fh);


# Expression is usually appended to other selectors
if (scalar(@xmm_reg) == 0) {
    die "ERROR: no region selections found\n";
} elsif (scalar(@xmm_reg) == 1) {
    print "&&$xmm_reg[0]\n";
} else {
    print "&&( " . join(" || ", @xmm_reg) . " )\n";
}

# Convert DS9 sky angle to XMM detector angle for one of MOS1, MOS2, or PN
#
# Note:
# +ve change in detector angle induces -ve change in sky angle because DETX/Y
# coordinates are inverted w.r.t sky
# 
# Conventions:
# DS9 WCS/fk5 angle is measured CCW from West in sky frame (DS9 +x).
# XMM DETX/Y angle is measured CCW from +DETX in detector frame.
# XMM position angle (PA) is measured CCW from North in sky frame (DS9 +y),
# and the PA vector strikes along MOS1 +DETY, MOS2 -DETX, and PN +DETX axes.
#
# References:
# http://xmm-tools.cosmos.esa.int/external/xmm_user_support/documentation/uhb/epic.html
# http://xmm-tools.cosmos.esa.int/external/xmm_user_support/documentation/uhb/posdet.html
sub sky2detangle {

    my $angle = $_[0];

    # Angle from celestial N to RGS dispersion axis, going E (CCW in sky)
    # RGS axis strikes along +DETY (MOS1), -DETX (MOS2), +DETX (PN)
    system "fkeypar $calinfoset PA_PNT";
    my $pos_ang = `pget fkeypar value`;

    # EMOS1, EMOS2, EPN
    system "fkeypar $calinfoset INSTRUME";
    my $instr= `pget fkeypar value`;
    ($instr) = $instr =~ /'([A-Za-z0-9]+)'/;  # Strip single quotes

    # sky_angle_from_pa_pnt = angle_ds9 - (PA_PNT + 90)
    # mos1_detang = -1 * sky_angle_from_pa_pnt + 90
    # mos2_detang = -1 * sky_angle_from_pa_pnt + 180
    # pn_detang = -1 * sky_angle_from_pa_pnt

    my $detangle;
    if ($instr eq "EMOS1") {
	$detangle = $pos_ang - $angle + 180;
    } elsif ($instr eq "EMOS2") {
	$detangle = $pos_ang - $angle - 90;
    } elsif ($instr eq "EPN") {
	$detangle = $pos_ang - $angle + 90;
    } else {
	die "Invalid INSTRUME $instr\n";
    }

    return $detangle;
}


# Convert DS9 ra/dec to XMM detector coordinates, for particular obsid/exposure
# (specified by script input $calinfoset), using SAS task 'esky2det'
#
# Input: ds9 formatted RA / dec (i.e., colon delimited HMS/DMS)
# Output: DETX/DETY coordinates for $calinfoset obsid/exposure
sub radec2detxy {

    my ($ra, $dec) = @_;
    $ra =~ s/([\d]+):([\d]+):([\d.]+)/$1h$2m$3s/;  # Convert colons to h/m/s
    $dec =~ s/([\d]+):([\d]+):([\d.]+)/$1d$2m$3s/;  # Convert colons to d/m/s

    my $cmd = "esky2det datastyle='user' outunit='det' withheader='no' -V 0"
	. " ra='$ra' dec='$dec' calinfoset='$calinfoset' checkfov='no'";
    my $result = `$cmd`;
    my ($detx, $dety) = ($result =~ /([0-9.-]+)\s+([0-9.-]+)/);

    return ($detx, $dety);
}

