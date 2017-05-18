# -*- coding: utf-8 -*-

import os
import argparse
from lxml import etree
from lxml.html.clean import Cleaner
import fnmatch
import time
import pandas as pd
import datetime


def timeit(method):
    """Time methods."""
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r %2.2f sec' %
              (method.__name__, te-ts))
        return result

    return timed


class AddMetadata(object):
    """Get proceedings of the European Parliament."""

    @timeit
    def __init__(self):
        self.cli()
        self.infiles = self.get_files(self.indir, self.pattern)
        self.n_proceedings = 0
        self.rm_a = Cleaner(remove_tags=['a'])
        self.main()

    def __str__(self):
        message = "Added metatadata to {} proceedings!".format(
            str(self.n_proceedings))
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

    def read_xml(self, infile):
        """Parse a HTML file."""
        with open(infile, encoding='utf-8', mode='r') as input:
            return etree.parse(input)

    def serialize(self, infile, root):
        ofile_name = os.path.splitext(os.path.basename(infile))[0]
        ofile_path = os.path.join(self.outdir, ofile_name+'.xml')
        xml = etree.tostring(
            root,
            encoding='utf-8',
            xml_declaration=True,
            pretty_print=True).decode('utf-8')
        with open(ofile_path, mode='w', encoding='utf-8') as ofile:
            ofile.write(xml)
        pass

    def main(self):
        meps = pd.read_csv(
            self.meps,
            sep='\t',
            encoding='utf-8',
            dtype={'id': str}
            )
        if self.n_parties is not None:
            n_parties = pd.read_csv(
                self.n_parties,
                sep='\t',
                encoding='utf-8',
                parse_dates=[1, 2],
                infer_datetime_format=True,
                dtype={'id': str}
                )
        if self.p_groups is not None:
            p_groups = pd.read_csv(
                self.p_groups,
                sep='\t',
                encoding='utf-8',
                parse_dates=[2, 3],
                infer_datetime_format=True,
                dtype={'id': str}
                )
        for infile in self.infiles:
            print(infile)
            tree = self.read_xml(infile)
            root = tree.getroot()
            fdate = datetime.datetime.strptime(
                root.attrib['date'], '%Y-%m-%d').date()
            interventions = tree.xpath(
                './/intervention[@speaker_id!="photo_generic"]')
            for i in interventions:
                metadata = []
                speaker_id = i.attrib['speaker_id']
                idx_meps = meps.loc[meps['id'] == speaker_id].index.tolist()[0]
                metadata.append(('name', meps.get_value(idx_meps, 'name')))
                metadata.append((
                    'nationality',
                    meps.get_value(idx_meps, 'nationality')))
                metadata.append((
                    'birth_date',
                    meps.get_value(idx_meps, 'birth_date')))
                metadata.append((
                    'birth_place',
                    meps.get_value(idx_meps, 'birth_place')))
                if self.n_parties is not None:
                    idx_n_party = n_parties.loc[(n_parties['id'] == speaker_id) & (n_parties['s_date'] <= fdate) & (n_parties['e_date'] >= fdate)].index.tolist()
                    if len(idx_n_party) > 0:
                        idx_n_party = idx_n_party[0]
                        metadata.append(('n_party', n_parties.get_value(idx_n_party, 'n_party')))
                if self.p_groups is not None:
                    idx_p_group = p_groups.loc[(p_groups['id'] == speaker_id) & (p_groups['s_date'] <= fdate) & (p_groups['e_date'] >= fdate)].index.tolist()
                    if len(idx_p_group) > 0:
                        idx_p_group = idx_p_group[0]
                        metadata.append((
                            'p_group',
                            p_groups.get_value(idx_p_group, 'p_group')))
                        metadata.append((
                            'm_state',
                            p_groups.get_value(idx_p_group, 'm_state')))
                for a in metadata:
                    if type(a[1]) is not float:
                        i.attrib[a[0]] = a[1]
            self.serialize(infile, root)
            self.n_proceedings += 1
        pass

    def cli(self):
        """CLI parses command-line arguments"""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-m", "--meps",
            required=True,
            help="path to the MEPs' metadata file.")
        parser.add_argument(
            '-n', "--n_parties",
            required=False,
            default=None,
            help="path to the national parties metadata file.")
        parser.add_argument(
            "-g", "--p_groups",
            required=False,
            default=None,
            help="path to the political groups file.")
        parser.add_argument(
            "-x", "--xml",
            required=True,
            help="path to the directory with the xml files we want to add\
                metadata.")
        parser.add_argument(
            "-o", "--output",
            required=True,
            help="path to the output directory.")
        parser.add_argument(
            '-p', "--pattern",
            required=False,
            default="*.xml",
            help="glob pattern to filter files.")
        args = parser.parse_args()
        self.meps = args.meps
        self.n_parties = args.n_parties
        self.p_groups = args.p_groups
        self.indir = args.xml
        self.outdir = args.output
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        self.pattern = args.pattern
        pass


print(AddMetadata())
