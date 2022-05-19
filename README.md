# Python CLI for webAlignToolkit

Align Parallel Corpora using http://phraseotext.univ-grenoble-alpes.fr/webAlignToolkit/

## Setup

* Install requirements
```pip install -r requirements.txt```


## Usage

```console

usage: align.py [-h] [-o OUTPUT] language_file [language_file ...]

Align Sentences using WebAlignToolkit

positional arguments:
  language_file         Language Files

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output
```

**Note**

* Language files must start with `<lang_id>-`, e.g. `sa-42.txt`
* Output is written to a `.xlsx` file

## Example

`python align.py data/sa-12.txt data/kn-12.txt_out data/hi-12.txt_out -o output.xlsx`

**Workflow**

* Identifies the languages from filenames
* Reads file contents
* Sends an HTTP POST request to [webAlignToolkit](http://phraseotext.univ-grenoble-alpes.fr/webAlignToolkit/)
* Receives output (TMX URL)
* Fetches TMX content using another HTTP GET request
* Parses TMX content
* Exports aligned data as a spreadsheet
