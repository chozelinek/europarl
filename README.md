# EuroParl

This is a toolkit to create a comparable/parallel corpus made of European Parliament's proceedings enriched with speakers' metadata.

## Contents

- `LICENSE`, MIT license.
- `README.md`, this file.
- `add_metadata.py`, script to add MEPs metadata (CSV) to proceedings (XML).
- `dates.EN.txt`, one date per line in format YYYY-MM-DD.
- `getmeps.py`, script to scrap MEPs information.
- `getproceedings.py`, script to scrap Proceedings of the European Parliament.
- `meps_ie.py`, script to extract MEPs metadata from HTML to CSV.
- `proceedings_txt.py`, script to extract text from HTML proceedings.
- `proceedings_xml.py`, script to model as XML interventions in HTML proceedings.

## Requirements

You need `python3` and the following modules:

- `lxml`
- `requests`
- `pandas`
- `dateparser`

## Scrapping European Parliament's proceedings

### Get proceedings in HTML

We use the script `getproceedings.py` to:

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
# to get the proceedings for English
python getproceedings.py -o html/EN -l EN
# to get the proceedings for Spanish
python getproceedings.py -o html/ES -l ES -d dates.EN.txt
# to get the proceedings for German
python getproceedings.py -o html/DE -l DE -d dates.EN.txt
```

- `-o` is the path to the output folder to save the downloaded files.
- `-d` is the path to a plain text file, with one date per line in format YYYY-MM-DD.

## Scrapping MEPs information

The European Parliament website maintains a database with all Members of the European Parliament.

### Get the metadata in HTML

We use the script `getmeps.py` to download as HTML the metadata of all MEPs.

1. The script retrieves an XML file containing a list of all MEPs full names and unique IDs: <http://www.europarl.europa.eu/meps/en/xml.html?query=full&filter=all&leg=0>;
1. For each MEP, generate an URL to the actual HTML file containing the metadata: <http://www.europarl.europa.eu/meps/en/33569/33569_history.html>;
1. request it;
1. download and proceed with the next.

#### Usage

```shell
python getmeps.py -o meps
```

- `-o` is the path to the output folder to save the downloaded files.

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
python proceedings_txt.py -i html/EN -o txt/EN
```

## Transforming HTML proceedings into XML

### Usage

```shell
python proceedings_xml.py -i html/EN -o xml/EN/ -l EN
```

## Extracting MEPs information from HTML

### Usage

```shell
python meps_ie.py -i html/MEPS/ -o xml/MEPS/
```

## Adding MEPs' metadata to XML proceedings

### Usage

```shell
python add_metadata.py -m xml/MEPS/meps.csv -n xml/MEPS/national_parties.csv -g xml/MEPS/political_groups.csv -x xml/EN/ -p "*.xml" -o xml_metadata/EN
```
