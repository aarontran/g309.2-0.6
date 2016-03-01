#!/data/mpcrit4/bin/perl

# Parse output from XSPEC (manually obtained with iplot; wdata; or via PyXSPEC)
# and dump to multiple whitespace-delimited plaintext files

use 5.010;
use strict;
use warnings;

use Getopt::Long;

my ($opt_help, $opt_usage, $opt_verbose);
my ($opt_in, $opt_out);
GetOptions('help|h'    => \$opt_help,
           'usage|u'   => \$opt_usage,
           'verbose|v' => \$opt_verbose,
           'in|i=s'    => \$opt_in,
           'out|o=s'   => \$opt_out,
          ) or help(1);

help(0) if ($opt_help or $opt_usage);
help(1) if (! defined $opt_in);
help(1) if (! defined $opt_out);

# "Global" variable: output filename format
my $f_out_fmt = $opt_out . "_%02d.dat";


# Start numbering from one to match XSPEC convention
my $i = 1;  
my ($fh_out, $f_name) = make_fh($i);
vprint("Writing $f_name...");

open(my $fh_in, "<", $opt_in) or die "Cannot open $opt_in to read: $!";
while (<$fh_in>) {

    if ($_ =~ /^(NO\s*)+/) {  # Split on "NO NO NO NO NO ..."
	close($fh_out);
	vprint(" done.\n");

	# Increment file number, name
	$i++;
	($fh_out, $f_name) = make_fh($i);
	vprint("Writing $f_name...");
    }

    # Skip lines that don't start with a number
    print $fh_out $_ if ($_ =~ /^[\d.]+\s+/);
}
close($fh_in);
close($fh_out);
vprint(" done.\n");

vprint("All done!\n");


# Input: file number
# Output: file handle for writing
sub make_fh {
    my $i = shift;
    die "Cannot handle >99 datasets" if $i >= 100;  # Just in case...

    my $f_out = sprintf $f_out_fmt, $i;
    open(my $fh_out, ">", $f_out) or die "Cannot open $f_out to write: $!";
    return $fh_out, $f_out;
}

# Input: line to print in verbose mode
sub vprint {
    print $_[0] if $opt_verbose;
}

# Input $_[0]: exit status
sub help {
    my $progname = $0;
    $progname =~ s/.*\///;
    say "Usage: $progname [-h] -i input_file -o output_file_stem";
    say "-i, --input: XSPEC iplot file dump (plaintext, QDP/PLT file)";
    say "-o, --out: output file stem; files will be named {out}_00.dat, _01.dat, ...";
    say "-h, --help: get help";
    say "-u, --usage: also get help";
    say "-v, --verbose: be chitchatty";
    exit $_[0];
}
