# -*- coding: utf-8 -*-

import os
import argparse
import requests
from lxml import etree
from io import BytesIO


class GetMeps(object):
    """Get metadata of MEPs."""

    def __init__(self):
        self.cli()
        self.main()

    def __str__(self):
        message = "{} MEPs' metadata files downloaded!".format(
            str(self.n_meps)
            )
        return message

    def main(self):
        all_meps_url = ("http://www.europarl.europa.eu/meps/en/xml.html" +
                        "?query=full&filter=all&leg=0")
        all_meps_r = requests.get(all_meps_url)
        all_meps_xml = all_meps_r.content
        all_meps = etree.parse(BytesIO(all_meps_xml))
        self.n_meps = 0
        url_pattern = ("http://www.europarl.europa.eu/meps/en/" +
                       "{}/{}_history.html")
        for mep in all_meps.xpath('//mep/id/text()'):
            url = url_pattern.format(mep, mep)
            r = requests.get(url)
            if r.status_code == requests.codes.ok:
                print(mep)
                ofname = "{}.html".format(mep)
                ofpath = os.path.join(self.outdir, ofname)
                with open(ofpath, mode='wb') as ohtml:
                    ohtml.write(r.content)
                self.n_meps += 1
        pass

    def cli(self):
        """CLI parses command-line arguments"""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-o", "--output",
            required=True,
            help="path to the output directory.")
        args = parser.parse_args()
        self.outdir = args.output
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        pass


print(GetMeps())
