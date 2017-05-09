# -*- coding: utf-8 -*-

import os
import argparse
import requests
from lxml import etree
from io import BytesIO
import fnmatch


class GetMeps(object):
    """Get metadata of MEPs."""

    def __init__(self):
        self.cli()
        self.n_meps = 0
        self.main()

    def __str__(self):
        message = "{} MEPs' metadata files downloaded!".format(
            str(self.n_meps)
            )
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

    def main(self):
        if self.fromfile is False:
            all_meps_url = ("http://www.europarl.europa.eu/meps/en/xml.html" +
                            "?query=full&filter=all&leg=0")
            all_meps_r = requests.get(all_meps_url)
            all_meps_xml = all_meps_r.content
            all_meps = etree.parse(BytesIO(all_meps_xml))
            all_mep_ids = all_meps.xpath('//id/text()')
            if self.resume is True:
                already_downloaded = self.get_files(self.outdir, "*.html")
                already_downloaded = [os.path.splitext(os.path.basename(x))[0] for x in already_downloaded]
                remaining_ids = set(all_mep_ids) - set(already_downloaded)
                ids_to_download = set(remaining_ids)
            else:
                remaining_ids = set(all_mep_ids)
                ids_to_download = set(remaining_ids)
        elif self.fromfile is not False:
            with open(self.fromfile, 'r', encoding='utf-8') as mep_ids_file:
                all_mep_ids = mep_ids_file.read()
            all_mep_ids = all_mep_ids.strip()
            remaining_ids = set(all_mep_ids.split('\n'))
            ids_to_download = set(remaining_ids)
        url_pattern = ("http://www.europarl.europa.eu/meps/en/" +
                       "{}/{}_history.html")
        for id in ids_to_download:
            print(id)
            url = url_pattern.format(id, id)
            r = requests.get(url)
            if r.status_code == requests.codes.ok:
                ofname = "{}.html".format(id)
                ofpath = os.path.join(self.outdir, ofname)
                with open(ofpath, mode='wb') as ohtml:
                    ohtml.write(r.content)
                self.n_meps += 1
                remaining_ids.remove(id)
        pass

    def cli(self):
        """CLI parses command-line arguments"""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-o", "--output",
            required=True,
            help="path to the output directory.")
        parser.add_argument(
            "-f", "--fromfile",
            required=False,
            default=False,
            help="path to a file containing a list of IDs to download.")
        parser.add_argument(
            "-r", "--resume",
            required=False,
            action="store_true",
            help="resume downloads from already downloaded files in output folder.")
        args = parser.parse_args()
        self.outdir = args.output
        self.fromfile = args.fromfile
        self.resume = args.resume
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        pass


print(GetMeps())
