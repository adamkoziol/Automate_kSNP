#!/usr/bin/env python

import os, glob, shutil, errno, re, time
# Argument parser for user-inputted values, and a nifty help menu
from argparse import ArgumentParser

#Parser for arguments
parser = ArgumentParser(description='Automates kSNP analyses')
parser.add_argument('-p', '--path', required=True, help='Specify path')

# Get the arguments into a list
args = vars(parser.parse_args())

# Define variables from the arguments - there may be a more streamlined way to do this
path = args['path']
# os.chdir(path)
# path = "/media/nas/akoziol/Pipeline_development/ePFGE/kSNP/Listeria/AllReference/referenceGenomes"
# path = "/media/nas/akoziol/Pipeline_development/ePFGE/kSNP/Listeria/2015-01-23/903_906"
# path = "/media/nas/akoziol/Pipeline_development/ePFGE/kSNP/Listeria/2015-01-30/943_944"
# path = "/media/nas/akoziol/Pipeline_development/ePFGE/kSNP/Listeria/type2/944_990"
# path = "/media/nas/akoziol/Pipeline_development/ePFGE/kSNP/Salmonella/994_910"
# path = "/media/nas/akoziol/Pipeline_development/ePFGE/kSNP/Listeria/2015-02-06/988_944"
# path = "/media/nas/akoziol/Pipeline_development/ePFGE/kSNP/Salmonella/2015-02-06/997_421"
# path = "/media/nas/akoziol/Pipeline_development/ePFGE/kSNP/Salmonella/2015-02-13/Seeds"
# path = "/media/nas/akoziol/Pipeline_development/ePFGE/kSNP/Salmonella/2015-02-13/15009_15005"
# path = "/media/nas/akoziol/Pipeline_development/ePFGE/kSNP/Listeria/2015-02-20/14145_1101"
# path = "/media/nas/akoziol/Pipeline_development/ePFGE/kSNP/Salmonella/2015-02-13/15009_910"
# path = "/media/nas/akoziol/Pipeline_development/ePFGE/kSNP/Listeria/type2"
# path = "/media/nas/akoziol/Pipeline_development/ePFGE/kSNP/Listeria/2015-02-27/1136_1101"
# path = os.getcwd()

os.chdir(path)

date = time.strftime("%Y-%m-%d")

def make_path(inPath):
    """from: http://stackoverflow.com/questions/273192/check-if-a-directory-exists-and-create-it-if-necessary \
    does what is indicated by the URL"""
    try:
        os.makedirs(inPath)
        # os.chmod(inPath, 0777)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


files = glob.glob("*_filteredAssembled.fasta")
# files = glob.glob("*.fasta")

if files:
    for genome in files:
        name = genome.replace("_filteredAssembled.fasta", "")
        # name = genome.replace(".fasta", "")
        make_path("%s/%s" % (path, name))
        shutil.move(genome, "%s/%s" % (path, name))
        print genome


folders = glob.glob("*/")

for folder in folders:
    # print folder
    if os.path.isdir(folder) and not "referenceGenomes" in folder and not "olderAnalysis" in folder:
        if not re.search("kSNP", folder):
            # if "SEQ-1133" in folder:
            # if os.path.isfile("%s/%s/%s_filteredAssembled.fasta" % (path, folder, folder)):
            print folder
            contigs = glob.glob("%s/%s/*filteredAssembled.fasta" % (path, folder))[0]
            # contigs = glob.glob("%s/%s/*.fasta" % (path, folder))[0]
            name = os.path.split(contigs)[1].replace("_filteredAssembled.fasta", "")
            # name = os.path.split(contigs)[1].replace(".fasta", "")
            mergeCommand = "/home/blais/Bioinformatics/kSNP2.1.2/merge_fasta_contigs %s > %s/%s/%s_merged.fasta" % (contigs, path, folder, name)
            print mergeCommand
            os.system(mergeCommand)
            shutil.copy("%s/%s/%s_merged.fasta" % (path, folder, name), path)

catCommand = "cat *_merged.fasta > genomes.fa"
nameCommand = "/home/blais/Bioinformatics/kSNP2.1.2/genome_names genomes.fa > names.txt"
kSNPCommand = "/home/blais/Bioinformatics/kSNP2.1.2/kSNP -f genomes.fa -d kSNP-outk51_%s -k 51 -p names.txt" % date

print catCommand
os.system(catCommand)
print nameCommand
os.system(nameCommand)
print kSNPCommand
os.system(kSNPCommand)


