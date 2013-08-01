#!/usr/bin/python

#This script is designed to take zone files exported from specific other DNS
#providers and modify them to a standard BIND style format that can be
#imported to DynECT. Symptoms of a malformed zonefile are lack of trailing
#periods on CNAME/SRV/MX records as well as other minor issues with SRV
#records.
#
#Usage: %python zonfile_repair.py FILES [-d FOLDER|--dir FOLDER |-b|-backup]
#
#Details:
#    	FILES		Accepts a single file of file pattern. No validation is done for valid zone file
#	-h, --help	Show help message and exit
#	-b, --backup	Create a backup of the zonefile before processing. Defaults directory is /BACKUP
#	-d, --dir	Defines the folder where backups should be placed instead of using /BACKUP
#
import os, re, sys, shutil, argparse

#Variables
opt_file = ''
file_string = ''
opt_dir = ''
opt_backup = True 

#Setup command line parameters
def GetOptions():
	parser = argparse.ArgumentParser(description='Process some integers.')
	opt_file = parser.add_argument('fileIn', help='Accepts a single file of file pattern. No validation is done for valid zone file')
	opt_backup = parser.add_argument('-b','--backup', dest='backup', action='store_true', help='Create a backup of the zone file before processing. Defaults directory is /BACKUP')
	opt_dir = parser.add_argument('-d','--dir', dest='directory', help='Defines the folder where backups should be placed instead of using /BACKUP')
	args = parser.parse_args()
	return args.fileIn, args.directory, args.backup

opt_file, opt_dir, opt_backup = GetOptions() #Set variables from input

#If backup is true but DIR isn't defined set to 'BACKUP' as default
if (opt_backup):	
	if not(opt_dir):
		opt_dir = 'BACKUP'

#Else if DIR exists but backup isn't set. Set it to true.
elif(opt_dir):
	opt_backup = True

#If backup is set, create the directory.
if(opt_backup):	
	if not (os.path.isdir(opt_dir)): #If the directory doesn't exist, create it
		os.mkdir( opt_dir, 0755 )
	
	try:	#Copying backup to directory defined with the filename with .bak appended to it
		shutil.copyfile(opt_file, opt_dir+'/'+os.path.basename(opt_file)+'.bak')
	except OSError as exc: # Python >2.5
        	if exc.errno == errno.EEXIST and os.path.isdir(path):
            		pass
        	else: raise

#Reading file in. Clean exit on EOF 
with open (opt_file, "r") as fr:
	#Replacing every line and adding it to file_string
	for line in fr:
		line = line.rstrip('\n')#Removing whitespace
		line.replace('\r$', '')#Remove windows style whitespace

		#Correct trailing period issues on these record types
        	match = re.search(r'\s+IN\s+CNAME\s+|\s+IN\s+MX\s+|\s+IN\s+SRV\s+', line)
		if (match):
			#Looking for @ in the line. If it exists, skip replace
			match = re.search(r'^\s?\@', line)
			if not (match):
				line = re.sub(r'(\s*(?:;.*))$', r'.\1', line)

		#Remove extraneous @ from these record types
		match = re.search(r'\s+IN\s+SRV\s+', line)
		if (match):
			line = re.sub(r'\.@', r'', line)
		#Building file.
		file_string += line + '\n'

#Writing new file
with open(opt_file, 'w') as fw:
	fw.write(file_string)

