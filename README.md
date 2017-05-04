# EuroParl

This is the creation of a parallel corpus where text and metadata are scrapped.

## Scrapping

<http://docs.python-guide.org/en/latest/scenarios/scrape/>

## Metadata

### MEPs

This XML file contains a list of all MEPs with their full name and unique ID:

<http://www.europarl.europa.eu/meps/en/xml.html?query=full&filter=all&leg=0>

Typical pattern to download information about MEPs:

<http://www.europarl.europa.eu/meps/en/33569/SYED_KAMALL_history.html>

This is also a valid pattern URL:

<http://www.europarl.europa.eu/meps/en/33569/33569_history.html>

- `query=full`: all available data.
- `filter=all`: all MEPs, alternatively, one can choose an alphabet letter (A, B, ...) to filter only speakers whose family name starts with that letter.
- `leg=0`: all legislatures, integers help to select a past legislature, if no value provided just current legislature.

<http://www.europarl.europa.eu/meps/en/xml.html?query=full&filter=all> yields basic metadata for current legislature.

We use the script `getmeps.py` to download as HTML the metadata of all meps listed in the XML file containing all MEPs' IDs.

```bash
python getmeps.py -o meps
```

### Other speakers

## Texts

### Get proceedings in HTML

Typical URL for the proceedings
<http://www.europarl.europa.eu/sides/getDoc.do?pubRef=-//EP//TEXT+CRE+20090505+ITEMS+DOC+XML+V0//EN&language=EN>

We use the script `getproceedings.py` to generate a range of dates, generate a URL, request it, if it exists, dowload the document, if not, proceed with the next.

```bash
python getproceedings.py -o html/EN -l EN
python getproceedings.py -o html/ES -l ES -d dates.EN.txt
```

## Processing

## Alignment
