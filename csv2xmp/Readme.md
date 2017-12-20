# csv2xmp
This script is used to enrich files with xmp metadata.
It takes the metadata from a csv file and writes it to the appropriate file.
The script crawls the target directory (parameter -d) and creates an index
for all files with the specified file extension (parameter -t). Then it
adds all the metadata in the csv to the appropriate file (matching by filename).
The mapping.py data contains the mapping between the source and the target
schema name. The provided mapping is for the DAI Core Metadata, e.g.
"01_Titel" is mapped to "dc:title".
Currently it is only tested and probably working for TIF & JPEG Files.

## Requirements:

### CSV metadate file
The csv file must contain a row named "Dateiname", which contains the correct
file name. Further it is expected to have TAB as the delimeter.

### Exempi

The tool exempi is used in the script and needs to be installed. For Mac using homebrew [1]:

```
brew install exempi
```

[1] https://brew.sh/index_de.html


### Python

* Python 2.7.14
* Pip

The python packages, that exceeds the python standard installations are listed in the requirements.txt and could be installed by:
```bash
pip install -r requirements.txt
```
Or directly, as it is just one package:
```bash
pip install python-xmp-toolkit==2.0.1
```

## Parameters:
```
 -c --csvfile= This parameter hands over the location of a csv file containing
  the extracted arachne image metadata
 -d --targetdirectory= This optional parameter is used to define the target
  directory, if it is in another location
 -t --filetype= This optional parameter is used to restrict the files by a
  specific file extension
```

## Examples:
```python
 python csv2xmp.py -c 'relative/path/metadata.csv' -d 'directory/'
 python csv2xmp.py -c images/test.csv -d /Users/phg/Documents/Development/ianus-scripts/csv2xmp/ -t JPG
```
