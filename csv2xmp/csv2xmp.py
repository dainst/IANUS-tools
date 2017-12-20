# author: Philipp Gerth (philipp.gerth@dainst.de)
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

#declaration of global variables
csvFile = ''
targetDir = ''
fileType = ''
overrideMD = 0


#logging basic configuration
logging.basicConfig(
    filename='csv2xmp.log',
    filemode='w',
    level=logging.DEBUG)

def metadataToFile(result, fileDict):
    for row in result:
        # TODO: Check for existing file in fileDict. If not existing, KeyError will be raised as well.
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
                        # if option -o: the original xmp data will be deleted
                        if overrideMD == 1:
                            xmp.delete_property(eval(value_split[0]), unicode(value_split[1], 'utf-8'))

                        xmp.set_property(eval(value_split[0]), unicode(value_split[1], 'utf-8'), unicode(row[key], 'utf-8') )
                except libxmp.XMPError:
                    errorMessage = 'Attribute ' + value.upper() + ' already existing for file: ' + row['Dateiname']
                    print errorMessage
                    logging.debug(errorMessage)
            # Save xmp metadata to the file
            xmpfile.put_xmp(xmp)
            xmpfile.close_file()

        except KeyError:
            errorMessage = 'KeyError found, while processing ' + row['Dateiname'] + '. Wrong mapping.py settings or missing File?'
            print errorMessage
            logging.debug(errorMessage)

def metadataByCsv(fileDict):

    with open(csvFile) as file:
        result = csv.DictReader(file, delimiter='\t')

        metadataToFile(result, fileDict)

def createFileDict(fileDict):

    for root, dirs, files in os.walk(targetDir, topdown=False):
        for name in files:
            if fileType in name:
                print os.path.join(root, name)
                fileDict[name] = os.path.join(root, name)

    print fileDict
    return fileDict

def main(argv):
    fileDict = {}

    try:
        opts, args = getopt.getopt(argv,"hc:d:t:o",["csvfile=","targetdirectory=","filetype="])
    except getopt.GetoptError:
        print 'csv2xmp.py -c <csvfile> -d <targetdirectory> [-t <filetype>] [-o]'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'csv2xmp.py -c <csvfile> -d <targetdirectory> [-t <filetype>]'
            sys.exit()
        elif opt in ("-c", "--csvfile"):
            global csvFile
            csvFile = arg
        elif opt in ("-d", "--targetdirectory"):
            global targetDir
            targetDir = arg
        elif opt in ("-t", "--filetype"):
            global fileType
            fileType = arg
        elif opt in ("-o", "--override"):
            global overrideMD
            overrideMD = 1

    if csvFile != "":
        print 'Csv input file is: ', csvFile
        createFileDict(fileDict)
        metadataByCsv(fileDict)

if __name__ == "__main__":
    main(sys.argv[1:])
