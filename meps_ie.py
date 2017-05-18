# -*- coding: utf-8 -*-

import os
import argparse
import datetime
from lxml import etree, html
from lxml.html.clean import Cleaner
import fnmatch  # To match files by pattern
import re
import time
import pandas as pd


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


class TransformHtmlProceedingsToXml(object):
    """Get proceedings of the European Parliament."""

    @timeit
    def __init__(self):
        self.cli()
        self.infiles = self.get_files(self.indir, self.pattern)
        self.n_proceedings = 0
        self.rm_a = Cleaner(remove_tags=['a'])
        self.main()

    def __str__(self):
        message = "Information for {} MEPs extracted!".format(
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

    def read_html(self, infile):
        """Parse a HTML file."""
        with open(infile, encoding='utf-8', mode='r') as input:
            return html.parse(input)

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

    def get_name(self, tree):
        name = tree.xpath('//li[@class="mep_name"]')[0]
        name = self.rm_a.clean_html(name)
        name = html.tostring(name).decode('utf-8')
        name = re.sub(r'[\t\n]', r'', name)
        name = name.split('<br>')
        name = [html.fromstring(x).text_content() for x in name]
        name = ' '.join(name)
        return name

    def get_nationality(self, tree):
        nationality = tree.find_class('nationality')[0]
        nationality = nationality.text.strip()
        return nationality

    def get_id(self, infile):
        id = os.path.splitext(os.path.basename(infile))[0]
        return id

    def parse_date(self, a_date, a_pattern):
        output = datetime.datetime.strptime(a_date, a_pattern).date()
        return output

    def get_birth(self, tree):
        birth = tree.xpath('.//span[@class="more_info"]')
        birth_date = None
        birth_place = None
        death_date = None
        death_place = None
        for i in birth:
            if i.text is not None:
                birth_text = re.sub(r'[\t\n]', r'', i.text)
                birth_text = birth_text.strip()
                if re.match(r'^Date of birth: (.+?), (.+)$', birth_text):
                    info = re.match(
                        r'^Date of birth: (.+?), (.+)$', birth_text)
                    birth_date = self.parse_date(info.group(1), "%d %B %Y")
                    birth_place = info.group(2)
                elif re.match(r'^Date of birth: (.+?)$', birth_text):
                    info = re.match(r'^Date of birth: (.+?)$', birth_text)
                    birth_date = self.parse_date(info.group(1), "%d %B %Y")
                    birth_place = None
                elif re.match(r'^Date of death: (.+?), (.+)$', birth_text):
                    info = re.match(
                        r'^Date of death: (.+?), (.+)$', birth_text)
                    death_date = self.parse_date(info.group(1), "%d %B %Y")
                    death_place = info.group(2)
                elif re.match(r'^Date of death: (.+?)$', birth_text):
                    info = re.match(r'^Date of death: (.+?)$', birth_text)
                    death_date = self.parse_date(info.group(1), "%d %B %Y")
                    death_place = None
        return birth_date, birth_place, death_date, death_place

    def get_political_groups(self, tree, id):
        political_groups = tree.xpath('.//div[@class="boxcontent nobackground"]/h4[contains(., "Political groups")]/following-sibling::ul[1]//li')
        output = []
        for i in political_groups:
            info = i.text
            info = re.sub(r'\n', r'', info)
            info = re.sub(r'\t+', r'\t', info)
            info = re.sub(r' \t/ ', r'\t', info)
            info = re.sub(r'\t:\t', r'\t', info)
            info = re.sub(r' - ', r'\t', info)
            info = re.sub(r'\t$', r'', info)
            info = info.strip()
            info = info.split('\t')
            info = [x.strip() for x in info]
            m_state = i.attrib['class']
            s_date = self.parse_date(info[0], "%d.%m.%Y")
            if info[1] == '...':
                e_date = self.date
            else:
                e_date = self.parse_date(info[1], "%d.%m.%Y")
            p_group = info[2]
            p_group_role = info[3]
            output.append({
                'id': id,
                'm_state': m_state,
                's_date': s_date,
                'e_date': e_date,
                'p_group': p_group,
                'p_group_role': p_group_role})
        return output

    def get_national_parties(self, tree, id):
        political_groups = tree.xpath('.//div[@class="boxcontent nobackground"]/h4[contains(., "National parties")]/following-sibling::ul[1]//li')
        output = []
        for i in political_groups:
            info = i.text
            info = re.sub(r'\n', r'', info)
            info = re.sub(r'\t+', r'\t', info)
            info = re.sub(r' \t/ ', r'\t', info)
            info = re.sub(r'\t:\t', r'\t', info)
            info = re.sub(r' - ', r'\t', info)
            info = re.sub(r'\t$', r'', info)
            info = info.strip()
            info = info.split('\t')
            info = [x.strip() for x in info]
            s_date = self.parse_date(info[0], "%d.%m.%Y")
            if info[1] == '...':
                e_date = self.date
            else:
                e_date = self.parse_date(info[1], "%d.%m.%Y")
            n_party = info[2]
            output.append({
                'id': id,
                's_date': s_date,
                'e_date': e_date,
                'n_party': n_party})
        return output

    def extract_info(self, infile):
        id = self.get_id(infile)
        tree = self.read_html(infile).getroot()
        name = self.get_name(tree)
        nationality = self.get_nationality(tree)
        birth_date, birth_place, death_date, death_place = self.get_birth(tree)
        self.meps[id] = {
            'name': name,
            'nationality': nationality,
            'birth_date': birth_date,
            'birth_place': birth_place,
            'death_date': death_date,
            'death_place': death_place
            }
        self.political_groups = (
            self.political_groups + self.get_political_groups(tree, id))
        self.national_parties = (
            self.national_parties + self.get_national_parties(tree, id))
        pass

    def serialize_dict_of_dicts(self, dict_of_dicts, ofile_name):
        df = pd.DataFrame.from_dict(dict_of_dicts, orient='index')
        opath = os.path.join(self.outdir, ofile_name)
        df.to_csv(
            opath,
            sep='\t',
            mode='w',
            encoding='utf-8',
            index_label='id')
        pass

    def serialize_list_of_dicts(self, list_of_dicts, ofile_name, col_order):
        df = pd.DataFrame(list_of_dicts)
        df = df[col_order]
        opath = os.path.join(self.outdir, ofile_name)
        df.to_csv(opath, sep='\t', mode='w', encoding='utf-8', index=False)
        pass

    def main(self):
        self.meps = {}
        self.political_groups = []
        self.national_parties = []
        for infile in self.infiles:
            print(infile)
            if self.date is None:
                self.date = datetime.datetime.fromtimestamp(
                    os.path.getmtime(infile)).date()
            self.extract_info(infile)
            self.n_proceedings += 1
        self.serialize_dict_of_dicts(self.meps, 'meps.csv')
        self.serialize_list_of_dicts(
            self.political_groups,
            'political_groups.csv',
            ['id', 'm_state', 's_date', 'e_date', 'p_group', 'p_group_role'])
        self.serialize_list_of_dicts(
            self.national_parties,
            'national_parties.csv',
            ['id', 's_date', 'e_date', 'n_party'])
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
        parser.add_argument(
            '-d', "--date",
            required=False,
            default=None,
            help="date of download of HTML files.")
        args = parser.parse_args()
        self.indir = args.input
        self.outdir = args.output
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        self.pattern = args.pattern
        self.date = args.date
        pass


print(TransformHtmlProceedingsToXml())
