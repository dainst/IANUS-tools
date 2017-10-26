# author: Philipp Gerth
#
# The script is used to enrich files with xmp metadata.
# It takes the metadata from a csv file and writes it to the appropriate file.
# The csv file must contain a row named "Dateiname", which contains the correct
# file name. Further it is expected to have TAB as the delimeter.
#
# Parameters:
# -c --csvfile= This parameter hands over the location of a csv file containing
#  the extracted arachne image metadata
# -d --targetdirectory= This optional parameter is used to define the target
#  directory, if it is in another location
# -t --filetype= This optional parameter is used to restrict the files by a
#  specific file extension
#
# Examples:
#
# python csv2xmp.py -c 'relative/path/metadata.csv' -d 'directory/'
# python csv2xmp.py -c images/test.csv -d /Users/phg/Documents/Development/ianus-scripts/csv2xmp/ -t JPG

import mapping
import libxmp
import sys, getopt
import csv
import os
import logging
from libxmp.consts import XMP_NS_DC as dc
from libxmp.consts import XMP_NS_Photoshop as photoshop
from libxmp.consts import XMP_NS_IPTCCore as Iptc4xmpCore

#logging basic configuration
logging.basicConfig(
    filename='csv2xmp.log',
    filemode='w',
    level=logging.DEBUG)

def metadataToFile(result, targetDir, fileDict):
    for row in result:
        try:
            path = fileDict[row['Dateiname']]
            print("------------------------------")
            print(path)
            xmpfile = libxmp.XMPFiles( file_path=path, open_forupdate=True )
            xmp = xmpfile.get_xmp()

            # Edit each of the xmp attributes of the image
            for key, value in mapping.mapping.items():
                try:
                    if row[key] != "":
                        value_split = value.strip().split(':', 1)
                        print (row[key])
                        print (xmp)
                        xmp.set_property(eval(value_split[0]), unicode(value_split[1], 'utf-8'), unicode(row[key], 'utf-8') )
                except libxmp.XMPError:
                    errorMessage = 'Attribute ' + value.upper() + ' already existing for file: ' + row['Dateiname']
                    print errorMessage
                    logging.debug(errorMessage)
            # Save xmp metadata to the file
            xmpfile.put_xmp(xmp)
            xmpfile.close_file()

        except KeyError:
            errorMessage = 'Missing file for metadata entry: ' + row['Dateiname']
            print errorMessage
            logging.debug(errorMessage)

def metadataByCsv(file, targetDir, fileDict):

    with open(file) as csvfile:
        result = csv.DictReader(csvfile, delimiter='\t')

        metadataToFile(result, targetDir, fileDict)

def createFileDict(targetDir, fileType, fileDict):

    for root, dirs, files in os.walk(targetDir, topdown=False):
        for name in files:
            if fileType in name:
                print os.path.join(root, name)
                fileDict[name] = os.path.join(root, name)

    print fileDict
    return fileDict

def main(argv):
    csvFile = ''
    targetDir = ''
    fileType = ''
    fileDict = {}

    try:
        opts, args = getopt.getopt(argv,"hc:d:t:",["csvfile=","targetdirectory=","filetype="])
    except getopt.GetoptError:
        print 'csv2xmp.py -c <csvfile> -d <targetdirectory> [-t <filetype>]'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'csv2xmp.py -c <csvfile> -d <targetdirectory> [-t <filetype>]'
            sys.exit()
        elif opt in ("-c", "--csvfile"):
            csvFile = arg
        elif opt in ("-d", "--targetdirectory"):
            targetDir = arg
        elif opt in ("-t", "--filetype"):
            fileType = arg

    if csvFile != "":
        print 'Csv input file is: ', csvFile
        createFileDict(targetDir, fileType, fileDict)
        metadataByCsv(csvFile, targetDir, fileDict)

if __name__ == "__main__":
    main(sys.argv[1:])
