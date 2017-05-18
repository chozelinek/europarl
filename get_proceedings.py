# -*- coding: utf-8 -*-

import os
import argparse
import requests
import datetime


class GetProceedings(object):
    """Get proceedings of the European Parliament."""

    def __init__(self):
        self.cli()
        self.main()

    def __str__(self):
        message = "{} EuroParl's {} proceedings downloaded!".format(
            str(self.n_proceedings),
            self.language)
        return message

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

    def main(self):
        self.n_proceedings = 0
        url_pattern = ("http://www.europarl.europa.eu/sides/getDoc.do?pubRef" +
                       "=-//EP//TEXT+CRE+{}+ITEMS+DOC+XML+V0//{}&language={}")
        if self.dates is None:
            step = datetime.timedelta(days=1)
            dates = []
            while self.start_date <= self.end_date:
                date_as_string = self.start_date.strftime('%Y%m%d')
                url = url_pattern.format(
                    date_as_string,
                    self.language,
                    self.language)
                r = requests.get(url)
                if r.status_code == requests.codes.ok:
                    print(date_as_string)
                    dates.append(self.start_date.strftime('%Y-%m-%d'))
                    ofname = "{}.{}.html".format(date_as_string, self.language)
                    ofpath = os.path.join(self.outdir, ofname)
                    with open(ofpath, mode='wb') as ohtml:
                        ohtml.write(r.content)
                    self.n_proceedings += 1
                self.start_date += step
            dates = '\n'.join(dates)
            with open('dates.{}.txt'.format(self.language), mode='w',
                      encoding='utf-8') as fdates:
                fdates.write(dates)
        else:
            dates = self.parse_dates()
            for d in dates:
                date_as_string = d.strftime('%Y%m%d')
                url = url_pattern.format(
                    date_as_string,
                    self.language,
                    self.language)
                r = requests.get(url)
                if r.status_code == requests.codes.ok:
                    print(date_as_string)
                    ofname = "{}.{}.html".format(date_as_string, self.language)
                    ofpath = os.path.join(self.outdir, ofname)
                    with open(ofpath, mode='wb') as ohtml:
                        ohtml.write(r.content)
                self.n_proceedings += 1
        pass

    def cli(self):
        """CLI parses command-line arguments"""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-o", "--output",
            required=True,
            help="path to the output directory.")
        parser.add_argument(
            "-l", "--language",
            required=True,
            choices=['en', 'es', 'de', 'fr', 'it'],
            help="version to be downloaded.")
        parser.add_argument(
            '-s', "--startdate",
            required=False,
            type=self.valid_date,
            default=datetime.datetime(1999, 7, 20),
            help="The Start Date - format YYYY-MM-DD")
        parser.add_argument(
            '-e', "--enddate",
            required=False,
            type=self.valid_date,
            default=datetime.datetime(2012, 11, 22),
            help="The Start Date - format YYYY-MM-DD")
        parser.add_argument(
            '-d', "--dates",
            required=False,
            help=("path to file containing one date per line" +
                  "in format YYYY-MM-DD.")
        )
        args = parser.parse_args()
        self.outdir = args.output
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        self.language = args.language.upper()
        self.start_date = args.startdate
        self.end_date = args.enddate
        self.dates = args.dates
        pass


print(GetProceedings())
