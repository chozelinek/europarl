# -*- coding: utf-8 -*-

import os
import argparse
import datetime
from lxml import etree
import fnmatch  # To match files by pattern
import re


class TransformHtmlProceedingsToTxt(object):
    """Get proceedings of the European Parliament."""

    def __init__(self):
        self.cli()
        self.infiles = self.get_files(self.indir, self.pattern)
        self.main()

    def __str__(self):
        message = "{} EuroParl's {} proceedings transformed!".format(
            str(self.n_proceedings),
            self.language)
        return message
    
    def get_files(self, directory, fileclue):
        """Get all files in a directory matching a pattern.
        
        Keyword arguments:
        directory -- a string for the input folder path
        fileclue -- a string as glob pattern
        """
        matches = []
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, fileclue):
                matches.append(os.path.join(root, filename))
        return matches

    def valid_date(self, s):
        try:
            return datetime.datetime.strptime(s, "%Y-%m-%d")
        except ValueError:
            msg = "Not a valid date: '{0}'.".format(s)
            raise argparse.ArgumentTypeError(msg)

    def parse_dates(self):
        with open(self.dates, mode='r', encoding='utf-8') as fdates:
            strdates = fdates.read()
            strdates = strdates.strip('\n')
        dates = [datetime.datetime.strptime(x, "%Y-%m-%d")
                 for x in strdates.split('\n')]
        return dates
    
    def read_xml(self, infile):
        """Parse a XML file."""
        parser = etree.XMLParser(remove_blank_text=True)
        with open(infile, encoding='utf-8',mode='r') as input:
            return etree.parse(input, parser)
        
    def serialize(self, a_string, infile):
        """Serialize output.
        
        Keyword arguments:
        tree_as_string -- tree as string
        infile -- path to the input file as string
        """
#         if not os.path.exists(self.outdir):
#             os.makedirs(self.outdir)
        outpath = os.path.join(  # output path
            self.outdir,
            os.path.splitext(os.path.basename(infile))[0]+'.'+'txt')  # depending on the output formats able to choose output extension
        with open(outpath, mode='w', encoding='utf8') as outfile:
            outfile.write(a_string)
        pass
    

    def main(self):
        self.n_proceedings = 0
        for infile in self.infiles:
            print(infile)
            tree = self.read_xml(infile)
            all_text = tree.xpath('//text()')
            all_text = [x.strip() for x in all_text]
            all_text = '\n'.join(all_text)
            all_text = re.sub(r' +\n', r'\n', all_text)
            all_text = re.sub(r'\n{3,}', r'\n\n\n', all_text)
            all_text = re.sub(r'\n(\(..\)\n)', r' \1', all_text)
            all_text = re.sub(r'\n\)', r')', all_text)
            all_text = re.sub(r'\(\n', r'(', all_text)
            all_text = re.sub(r',\n\n', r', ', all_text)
            all_text = re.sub(r'(\n\d+\.\d*\.?)\n', r'\1 ', all_text)
            all_text = re.sub(r'\n,', r',', all_text)
            all_text = re.sub(r'\[\n', r'[', all_text)
            all_text = re.sub(r'\n\]', r']', all_text)
            self.serialize(all_text, infile)
            
#         url_pattern = ("http://www.europarl.europa.eu/sides/getDoc.do?pubRef" +
#                        "=-//EP//TEXT+CRE+{}+ITEMS+DOC+XML+V0//{}&language={}")
#         if self.dates is None:
#             step = datetime.timedelta(days=1)
#             dates = []
#             while self.start_date <= self.end_date:
#                 date_as_string = self.start_date.strftime('%Y%m%d')
#                 url = url_pattern.format(
#                     date_as_string,
#                     self.language,
#                     self.language)
#                 r = requests.get(url)
#                 if r.status_code == requests.codes.ok:
#                     print(date_as_string)
#                     dates.append(self.start_date.strftime('%Y-%m-%d'))
#                     ofname = "{}.{}.html".format(date_as_string, self.language)
#                     ofpath = os.path.join(self.outdir, ofname)
#                     with open(ofpath, mode='wb') as ohtml:
#                         ohtml.write(r.content)
#                     self.n_proceedings += 1
#                 self.start_date += step
#             dates = '\n'.join(dates)
#             with open('dates.{}.txt'.format(self.language), mode='w',
#                       encoding='utf-8') as fdates:
#                 fdates.write(dates)
#         else:
#             dates = self.parse_dates()
#             for d in dates:
#                 date_as_string = d.strftime('%Y%m%d')
#                 url = url_pattern.format(
#                     date_as_string,
#                     self.language,
#                     self.language)
#                 r = requests.get(url)
#                 if r.status_code == requests.codes.ok:
#                     print(date_as_string)
#                     ofname = "{}.{}.html".format(date_as_string, self.language)
#                     ofpath = os.path.join(self.outdir, ofname)
#                     with open(ofpath, mode='wb') as ohtml:
#                         ohtml.write(r.content)
            self.n_proceedings += 1
        pass

    def cli(self):
        """CLI parses command-line arguments"""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-i", "--input",
            required=True,
            help="path to the input directory.")
        parser.add_argument(
            "-o", "--output",
            required=True,
            help="path to the output directory.")
        parser.add_argument(
            '-p', "--pattern",
            required=False,
            default="*.html",
            help="glob pattern to filter files.")
        args = parser.parse_args()
        self.indir = args.input
        self.outdir = args.output
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        self.language = args.language
        self.start_date = args.startdate
        self.end_date = args.enddate
        self.dates = args.dates
        self.pattern = args.pattern
        print(self.pattern)
        pass


print(TransformHtmlProceedingsToTxt())
