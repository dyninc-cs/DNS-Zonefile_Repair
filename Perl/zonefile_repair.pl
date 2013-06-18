#!/usr/bin/perl

#This script is designed to take zone files exported from specific other DNS
#providers and modify them to a standard BIND style format that can be
#imported to DynECT. Symptoms of a malformed zonefile are lack of trailing
#periods on CNAME/SRV/MX records as well as other minor issues with SRV
#records.
#
#Usage: %perl zonfile_repair.pl FILES [-d FOLDER|--dir FOLDER |-b|-backup]
#
#Details:
#    FILES           Accepts a single file of file pattern.
#                    No validation is done for valid zone file
#    -h, --help      Show this help message and exit
#    -b, --backup    Create a backup of files before processing
#                    Defaults to /BACKUP
#	-d, --dir       Defines the folder where backups should be placed
#

use warnings;
use strict;
use Getopt::Long;

my $opt_backup;
my $opt_dir;
my $help;

GetOptions( 
	'backup' => \$opt_backup,
	'dir=s' => \$opt_dir,
	'help' => \$help,
);

#help message if -h is set
if ($help) {
	print "\nUsage: %perl zonfile_repair.pl FILES [-d FOLDER|--dir FOLDER |-b|-backup]\n\n" .
		"\tOptions:\n" .
		"\t-h, --help\tShow this help message and exit\n" .
		"\t-b, --backup\tCreate a backup of files before processing, defaults to /BACKUP\n" .
		"\t-d, --dir\tDefines the folder where backups should be placed (implies -b).\n\n";
	exit;
}

#define file backups if -b or -d is set
if ($opt_backup) {
	$opt_dir = 'BACKUP' unless ($opt_dir);	#define a default value for $opt_dir if it doesnt exist
}
else {
	$opt_backup = 1 if ($opt_dir);	#Defining backup directory implies backup
}


if ($opt_backup) {
	unless (-d $opt_dir) {	
		#if the folder does not exist, attempt to create it	
		#DIE if folder creation fails
		mkdir $opt_dir or die "Can not create folder $opt_dir.  Please check if you have the correct permissions";	
	}
	$^I = "$opt_dir/*.bak";	#set backup files to be written to this directory
}
else {
	$^I = '';	#disable file backup
}

while ( <> ) {	#process file/matching files

	my $line = $_;
	chomp $line;
	$line =~ s/\r$//;        #Remove possible windows style newlines

	#correct trailing period issues on these record types
	if ( $line =~ m/\s+IN\s+CNAME\s+|\s+IN\s+MX\s+|\s+IN\s+SRV\s+/ ) {	
		$line =~ s/(\s*(?:;.*)?)$/\.$1/ unless $line =~ /\@$/;
	}

	#Remove extraneous @ from these record types
	if ($line =~ /\s+IN\s+SRV\s+/ ) {
		$line =~ s/\.@//;
	}

	print $line;	#print edited lines into new file
	print "\n";

}
