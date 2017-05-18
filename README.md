# EuroParl

This is a complete pipeline to create a comparable/parallel corpus made of European Parliament's proceedings enriched with speakers' metadata.

This pipeline has been tested in macOS Sierra, it should work in UNIX too. Basically, Python 3 is required for almost every script. Some Python modules and/or tools might be needed too. Check specific requirements for each script.

Related projects:

- [LinkedEP](http://purl.org/linkedpolitics)/[The talk of Europe](http://www.talkofeurope.eu/): Plenary debates of the European Parliament as Linked Open Data.
- [CoStEP](http://pub.cl.uzh.ch/purl/costep): Corrected & Structured Europarl Corpus
- [Koehn's EuroParl](http://www.statmt.org/europarl): European Parliament Proceedings Parallel Corpus
- [ECPC](http://www.ecpc.uji.es): European Comparable and Parallel Corpora

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
- `treetagger.py`, script to tokenize, lemmatize and tag PoS using TreeTagger producing well-formed XML.

## The pipeline

You can find the complete pipeline to compile the EuroParl corpus in `compile.sh`.

1. Download proceedings in HTML with `get_proceedings.py`
1. Download MEPs metadata in HTML with `get_meps.py`
1. Extract MEPs' information in a CSV file with `meps_ie.py`
1. Model proceedings as XML with `proceedings_xml.py`
1. Filter out text units not in the expected language (e.g. Bulgarian text in the English version) with `langid_filter.py`
1. Add MEPs metadata to proceedings with `add_metadata.py`
1. Add sentence boundaries (if needed) with `add_sentences.py`
1. Annotate token, lemma, PoS with TreeTagger with `treetagger.py`
1. Separate originals from translations and even filter by native speakers with `translationese_filter.py`

## `add_metadata.py`

### What

It adds MEPs' metadata to interventions in the proceedings.
Be aware that not all speakers speaking before the European Parliament are MEPs. There are members of other European Institutions, representatives of national institutions, guests, etc. speaking here. There is currently no metadata for those but the information extracted from the very same proceedings.

### How

It reads 3 files containing the metadata:

- `meps.csv` which contains basic information about the MEP: id, name, nationality, birth date, birth place, death date, death place.
- `national_parties.csv` which contains political affiliation of the MEP in his/her country: id, start date, end date, and name of the party.
- `political_groups.csv` which contains political affiliation at the European Parliament: id, Member State, start date, end date, name of the group, role within the group.

For each proceeding in XML it retrieves all interventions whose speaker is an MEP. Then it adds relevant speaker's metadata to the intervention. By relevant we mean the valid information at the day of the session.

### Requirements

- Python 3
- lxml
- pandas

## `add_sentences.py`

### What

It splits text contained in a given XML element into sentences.

### How

Using NLTK Punkt Tokenizer.

For each XML file, extracts all elements containing text. Each unit is passed to the tokenizer. It returns a list of sentences, which are converted in subelements of the element which was containing the text.

### Requirements

- Python 3
- lxml
- [nltk](http://www.nltk.org) and the Punkt Tokenizer Models for [nltk.tokenize.punkt](http://www.nltk.org/_modules/nltk/tokenize/punkt.html), follow [Installing NLTK Data instructions](http://www.nltk.org/data.html).

## `compile.sh`

### What

It runs the whole pipeline in one shot.

### How

It is a shell script running a list of commands sequentially. If no arguments provided it runs the full pipeline for all the supported languages.

One can provide the `-l` language argument, to run the pipeline only on a particular language, and `-p` pattern argument, to restrict the processing to a year, month, day...

### Requirements

All the requirements listed in this section and a bash shell.

## `get_meps.py`

### What

It downloads the MEPs' information avaliable at the web of the European Parliament in HTML format.

### How

First, it gets a list of all MEPs (past and present).

For each item in this list, it generates an URL and it downloads the page which contains basic information and the history record of the speaker.

### Requirements

- Python 3
- lxml
- requests

## `get_proceedings.py`

### What

It downloads all the proceedings in a particular language version within a range of dates.

### How

If a file with dates is given it generates an URL for each date and downloads the proceedings in HTML format. If no file with dates is provided, it generates all possible dates within a range, and tries to download only those URLs returning a sucessful response.

### Requirements

- Python 3
- requests

## `langid_filter.py`

### What

Sometimes, interventions remain untranslated and thus their text appear in their original language. In order to avoid this noise, `langid_filter.py` identifies the most probable language of each text unit (namely paragraphs) and remove those paragraphs which are not in the expected language (e.g. Bulgarian fragments found in the English version).

### How

All paragraphs (or units containing the text to be analyzed) are retrieved.

Each unit is analyzed with to language identifiers available for Python: `langdetect` and `langid`. A series of heuristics are then used to exploit the output of the language analyzers:

If the expected language and the language identified by both tools is the same, the text is in the same language as the language of the version at stake.

If both tools agree in identifying the language which is different to the expected version, the text is in a different language as the expected one, and, thus, removed.

For cases where there is not a perfect agreement a few rules are formalized working fairly well.

### Requirements

- Python 3
- lxml
- langdetect
- langid

## `meps_ie.py`

### What

It extracts MEPs information from semistructured HTML and yields the information in tabular format.

### How

It reads each HTML instance, and using XPath and regular expressions it finds relevant information which is finally serialized as three CSV files:

- `meps.csv`
- `national_parties.csv`
- `political_groups.csv`

### Requirements

- Python 3
- lxml
- pandas

## `proceedings_xml.py`

### What

It extracts basic metadata about the parliamentary session, the structure of the text, and about the speakers and the source language of the utterances, and the actual text of the proceedings.

- text: a session of parliamentary debates, it contains one or more sections.
    - id: YYYYMMDD.XX, date and language
    - lang: 2-letter ISO code for the language version
    - date: YYYY-MM-DD
    - place
    - edition
- section: an agenda item
    - id: ID as in the HTML for reference
    - title: CDATA, text of the heading/headline.
- intervention
    - id: ID as in the HTML for reference
    - speaker_id: if MEMP unique  code
    - name
    - is_mep: True or False
    - mode: spoken, written
    - role: function  of the speaker at the moment of speaking
- p: paragraphs
    - sl: Source Language
    - PCDATA: actual text
- a: annotations
    - text: CDATA

### How

It reads each HTML file, and using XPath and regular expressions it maintains the structure of the debates, and extracts metatextual information about the SL, the speaker, etc.

### Requirements

- Python 3
- lxml
- regex
- dateparser

## `proceedings_txt.py`

### What

It extracts all the text in the HTML proceedings.

### How

It parses the HTML, extracts only text, and clean a bit the output.

### Requirements

- Python 3
- lxml

## `translationse_filter.py`

### What

It filters out interventions to get:

- only originals
- all translations
- the translations of a particular SL

### How

It reads proceedings in XML and outputs XML with only the relevant paragraphs and their corresponding ancestors.

If native speakers (defined here as someone holding the nationality of a country with the SL as official language), XML with MEPs metadata is required.

It ritrieves all intervention and filters out interventions to keep only:

1. originals: if `sl` == `lang`
2. translations: if `sl` != `lang` and `sl` != unknown
3. translations from language xx

### Requirements

- Python 3
- lxml

## `treetagger.py`

### What

It tokenizes, lemmatizes, tags PoS and splits into sentences a text.

### How

It reads an XML file and annotates the text contained in a given element. It cares of producing well-formed XML as output.

### Requirements

- nltk (if tagging sentences is required)
- treetaggerwrapper
- TreeTagger
- language parameters

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
