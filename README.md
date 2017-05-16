# EuroParl

This is a complete pipeline to create a comparable/parallel corpus made of European Parliament's proceedings enriched with speakers' metadata.

This pipeline has been tested in macOS Sierra, it should work in UNIX too. Basically, Python 3 is required for almost every script. Some Python modules and/or tools might be needed too. Check specific requirements for each script.

## Contents

- `localization`, resources for adaptation of scripts to different languages.
- `LICENSE`, MIT license.
- `README.md`, this file.
- `add_metadata.py`, script to add MEPs metadata (CSV) to proceedings (XML).
- `add_sentences.py`, script to split text in sentences with NLTK's Punkt tokenizer.
- `compile.sh`, script to run the whole pipeline to compile the EuroParl corpus.
- `dates.txt`, one date per line in format YYYY-MM-DD.
- `get_meps.py`, script to scrap MEPs information.
- `get_proceedings.py`, script to scrap Proceedings of the European Parliament.
- `langid_filter.py`, filter out paragraphs whose real language is not the expected (the same of the proceedings).
- `meps_ie.py`, script to extract MEPs metadata from HTML to CSV.
- `proceedings_txt.py`, script to extract text from HTML proceedings.
- `proceedings_xml.py`, script to model as XML text and metadata from HTML proceedings.
- `translationse_filter.py`, script to classify utterances as original, translations and even by native speaker.
- `treetagger.sh`, script to tokenize, lemmatize and tag PoS for texts.

## The pipeline

You can find the complete pipeline to compile the EuroParl corpus in `compile.sh`.

1. Download proceedings in HTML with `get_proceedings.py`
1. Download MEPs metadata in HTML with `get_meps.py`
1. Extract MEPs' information in a CSV file with `meps_ie.py`
1. Model proceedings as XML with `proceedings_xml.py`
1. Filter out text units not in the expected language (e.g. Bulgarian text in the English version) with `langid_filter.py`
1. Add MEPs metadata to proceedings with `add_metadata.py`
1. Add sentence boundaries (if needed) with `add_sentences.py`
1. Annotate token, lemma, PoS with TreeTagger with `treetagger.sh`
1. Separate originals from translations and even filter by native speakers with `translationese_filter.py`

## `add_metadata.py`

### Requirements

- Python 3
- lxml
- pandas

## `add_sentences.py`

### Requirements

- Python 3
- lxml
- [nltk](http://www.nltk.org) and the Punkt Tokenizer Models for [nltk.tokenize.punkt](http://www.nltk.org/_modules/nltk/tokenize/punkt.html), follow [Installing NLTK Data instructions](http://www.nltk.org/data.html).

## `compile.sh`

### Requirements

All the requirements listed in this section and a bash shell.

## `get_meps.py`

### Requirements

- Python 3
- lxml
- requests

## `get_proceedings.py`

### Requirements

- Python 3
- requests

## `langid_filter.py`

### Requirements

- Python 3
- lxml
- langdetect
- langid

## `meps_ie.py`

### Requirements

- Python 3
- lxml
- pandas

## `proceedings_xml.py`

### Requirements

- Python 3
- lxml
- regex
- dateparser

## `proceedings_txt.py`

### Requirements

- Python 3
- lxml

## `translationse_filter.py`

### Requirements

- Python 3
- lxml

## `treetagger.sh`

### Requirements

- TreeTagger
- Language parameters:
    - English
    - Spanish
    - German
- sed

## Scrapping European Parliament's proceedings

### Get proceedings in HTML

We use the script `get_proceedings.py` to:

1. generate a range of dates, or read from file,
1. for each date,
1. generate a URL,
1. request it,
1. if it exists,
    1. download the document,
1. else,
    1. proceed with the next date.

This is the typical URL for the proceedings of a given day (namely, May 5 2009): <http://www.europarl.europa.eu/sides/getDoc.do?pubRef=-//EP//TEXT+CRE+20090505+ITEMS+DOC+XML+V0//EN&language=EN>

#### Usage

```shell
# get proceedings for English with defaults
python get_proceedings.py -o /path/to/output/dir -l EN
# get proceedings for Spanish using a list of dates
python get_proceedings.py -o /path/to/output/dir -l ES -d dates.txt
# get proceedings for German using a range of dates between two values
python get_proceedings.py -o /path/to/output/dir -l DE -s 2000-01-01 -e 2004-07-01
```

## Scrapping MEPs information

The European Parliament website maintains a database with all Members of the European Parliament.

### Get the metadata in HTML

We use the script `get_meps.py` to download as HTML the metadata of all MEPs.

1. The script retrieves an XML file containing a list of all MEPs full names and unique IDs: <http://www.europarl.europa.eu/meps/en/xml.html?query=full&filter=all&leg=0>;
1. For each MEP, generate an URL to the actual HTML file containing the metadata: <http://www.europarl.europa.eu/meps/en/33569/33569_history.html>;
1. request it;
1. download and proceed with the next.

#### Usage

```shell
python get_meps.py -o /path/to/output/dir
```

#### Some notes on querying the database

- This is also a valid pattern URL for a MEP: <http://www.europarl.europa.eu/meps/en/33569/SYED_KAMALL_history.html>
- `query=full`: all available data. <http://www.europarl.europa.eu/meps/en/xml.html?query=full>
- `filter=all`: all MEPs, alternatively, one can choose an alphabet letter (A, B, ...) to filter only speakers whose family name starts with that letter. <http://www.europarl.europa.eu/meps/en/xml.html?query=full&filter=all> or <http://www.europarl.europa.eu/meps/en/xml.html?query=full&filter=C>
- `leg=0`: all legislatures, integers help to select a past legislature, if no value provided just current legislature. <http://www.europarl.europa.eu/meps/en/xml.html?query=full&filter=all&leg=0>
- <http://www.europarl.europa.eu/meps/en/xml.html?query=full&filter=all> yields basic metadata for current legislature.

## On web scrapping with Python

<http://docs.python-guide.org/en/latest/scenarios/scrape/>

## Extracting text from HTML proceedings

### Usage

```shell
python proceedings_txt.py -i /path/to/html -o /path/to/output
```

## Transforming HTML proceedings into XML

### Usage

```shell
python proceedings_xml.py -i /path/to/html -o /path/to/xml -l EN
```

## Filtering out text not in the expected language

### Usage

```shell
python langid_filter.py -i /path/to/xml -o /path/to/xml
```

## Extracting MEPs information from HTML

### Usage

```shell
python meps_ie.py -i /path/to/metadata/dir -o /path/to/output/dir
```

## Adding MEPs' metadata to XML proceedings

### Usage

```shell
python add_metadata.py -m /path/to/meps.csv -n /path/to/national_parties.csv -g /path/to/political_groups.csv -x /path/to/source/xml/dir -p "*.xml" -o /path/to/output/xml/dir
```

## Filtering text after *translationese* criteria: original, translations, and restrict to *native speakers*

### Usage

```shell
# English originals in English proceedings
python translationese_filter.py -i /path/to/english/proceedings -o /path/to/output/dir -l en

# All translations in English proceedings
python translationese_filter.py -i /path/to/english/proceedings -o /path/to/output/dir -l all

# Translations from English in Spanish proceedings
python translationese_filter.py -i /path/to/spanish/proceedings -o /path/to/output/dir -l en

# English originals in English proceedings by native speakers
python translationese_filter.py -i /path/to/english/proceedings -o /path/to/output/dir -l en -n
```
