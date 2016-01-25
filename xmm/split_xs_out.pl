#!/data/mpcrit4/bin/perl

# Parse output from XSPEC (iplot; wdata;) and dump to multiple
# whitespace-delimited plaintext files

use 5.010;
use strict;
use warnings;

use Getopt::Long;

my ($opt_help, $opt_in, $opt_out);
GetOptions('help|h'   => \$opt_help,
           'in|i=s'   => \$opt_in,
           'out|o=s'  => \$opt_out,
          ) or help(1);

help(0) if $opt_help;
help(1) if (! defined $opt_in);
help(1) if (! defined $opt_out);

my $f_out_fmt = $opt_out . "_%02d.dat";
my $i = 0;
my $f_out = sprintf $f_out_fmt, $i;
open(my $fh_out, ">", $f_out) or die "Cannot open $f_out to write: $!";
open(my $fh_in, "<", $opt_in) or die "Cannot open $opt_in to read: $!";

while (<$fh_in>) {
    # Separator between datasets
    if ($_ =~ /^(NO\s*)+/) {
	$f_out = sprintf $f_out_fmt, $i++;
	die if $i > 100;  # Just in case...
	say $_;  # TODO debug
	say $f_out;  # TODO debug
	close($fh_out);
	open($fh_out, ">", $f_out);
    }

    next if ($_ !~ /^[\d.]/);
}
close($fh_in);
close($fh_out);

# Input $_[0]: exit status
sub help {

    my $progname = $0;
    $progname =~ s/.*\///;

    say "Usage: $progname [-h] -i input_file -o output_file_stem";
    say "--help : get help";
    say "-i, --input : XSPEC iplot file dump";
    say "-o, --out : output file stem";

    exit $_[0];
}
