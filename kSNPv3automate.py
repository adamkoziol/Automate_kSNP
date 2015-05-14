#!/usr/bin/env python

# the above line is a shebang, it tells commandline this is a python file and to treat it as such

__author__ = 'austin'

import subprocess
import os
import sys
import re
from Bio import SeqIO
import shutil
import errno
import glob
import time

# Get a date variable for proper naming of folders
date = time.strftime("%Y-%m-%d")

from argparse import ArgumentParser

# Arg parse allows you to run this script from command line. format of a command should for example be as shown in next comment:
# $   kSNPautomate.py -p /home/austin/Genomes/Assembledpacbiow2miseq2015-03-26 -k 23 -o O157T3_k23
#Parser for arguments
parser = ArgumentParser(description='runs all kSNP on all fasta and fastq files in the specified directory. Raw fastq files are joined and converted to fasta')
parser.add_argument('-p', '--path', required=True, help='Specify directory where the files you wish to run are located. The directory should contain only files you wish to include in analysis')
parser.add_argument('-k', '--kvalue', required=False, default="51", help='Specify the desired k-value. Default is 51.')
parser.add_argument('-o', '--outfile', required=False, default=date, help='Name of output folder. Default is "report".')
# Get the arguments into a list
args = vars(parser.parse_args())

# Define variables from the arguments
# path is the location of the files. Should only include fasta and unjoined fastq files you'd like to include in the analysis
path = args['path']
# desired k-value
kvalue = (args['kvalue'])
# name of output folder
Outname = args['outfile']

# name of file created that contains a list of all files included in the analysis.
# Used bykSNP, also specifies name of each sequence (based of file name), separated from the path by a tab.
filelistfilename = "k%sRunlist" % kvalue
# list of all fasta and fastq files that will be run
Filestorun = []

# not used?
def make_path(inPath):
    """makes a new folder as specified"""
    # from: http://stackoverflow.com/questions/273192/check-if-a-directory-exists-and-create-it-if-necessary does what is
    # indicated by the URL inPath should be the directory you want it in/name of new folder
    try:
        os.makedirs(inPath)
        # os.chmod(inPath, 0777)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def Joinconvertfastq():
    """Joins paired end fastq files and converts them to fasta files through terminal (any matching fastq files in the
    folder). Requires that the two fastq files have R1 and R2 in them and an otherwise identical file name.
    Needs Adam's join_paired_ends.py script (may have to be added to path if you haven't done that yet) and fastx's
    fastq_to_fasta function. Adam's script is on Github, fastx is available online for free"""
    os.system("gunzip *.gz")
    # makes a list of all fastq files containing "R1" (ie one of the two read files for each paired end sequence)
    R1fastqfiles = glob.glob("*R1*.fastq")
    for R1file in R1fastqfiles:
        # takes the file name up to R1 to name the new file, joins the two fastq files, converts it to a fasta file, and renames it.
        fastqfile = R1file.split("R1")[0]
        fastqR1andR2 = glob.glob("%s*.fastq" % fastqfile)
        joinName = re.split("_S\d+_L001", R1file)[0]
        print "starting %s file joining and conversion" % joinName
        # runs Adam's join paired end script. Needs to be installed in PATH.
        # If it won't run try adding "python " before the command below.
        os.system("join_paired_ends.py %s %s > %s/%s_joined.fastq" % (fastqR1andR2[0], fastqR1andR2[1], path, joinName))
        # Needs fastx installed properly, or at least the fastq_to_fasta.py script
        os.system("fastq_to_fasta -n -i %s/%s_joined.fastq -o %s/%s_joined.fasta" % (path, joinName, path, joinName))
        os.remove("%s/%s_joined.fastq" % (path, joinName))
        # TODO: delete fastq joined file
        print "done joining/conversion"
    print "done all fastq joining and conversion"

def Writefilelist():
    """Makes a text file named k#Runlist"""
    # call Joinconvertfastq before calling this so all fastq and fasta are in the Filestorun list
    # Adds all fasta to the Filestorun list
    print "writing file list"
    Allfastas = glob.glob("*fasta")
    for fastafile in Allfastas:
        Filestorun.append(fastafile)
    filelistfilehandle = open("%s/%s" % (path, filelistfilename), "wb")
    for FILE in Filestorun:
        FILEname = FILE.split(".fas")[0]
        filelistfilehandle.write("%s/%s\t%s\n" % (path, FILE, FILEname))
    filelistfilehandle.close()
    print "done writing file list"

def RunkSNP(Ksize, filelist, outdirname):
    """Runs kSNP script on terminal as shown below. Specify a text file containing paths of files, tab, then name of
    genome ("filelist"). Has to be run while in the directory containing the filelist"""
    print "starting kSNP..."
    os.chdir(path)
    # /usr/local/kSNP3.0/
    subprocess.call(["tcsh", "/home/blais/Bioinformatics/kSNP/kSNP/kSNP3", "-in", filelist, "-k", Ksize, "-outdir", outdirname])
    #os.system("tcsh /usr/local/kSNP3.0/kSNP3 -in %s -k %s -outdir %s" % (filelist, Ksize, outdirname))
    os.chdir(path)
    print "...finished kSNP"

os.chdir(path)
Joinconvertfastq()
Writefilelist()
RunkSNP(kvalue, filelistfilename, Outname)
# Deletes the unnecessary file
print "deleting intermediate files"
os.remove("%s/fasta_list" % path)
os.chdir("%s/%s" % (path, Outname))
shutil.rmtree("%s/%s/TemporaryFilesToDelete" % (path, Outname))
print "finished"