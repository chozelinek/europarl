# -*- coding: utf-8 -*-

import os
import argparse
from lxml import etree
import fnmatch  # To match files by pattern
import time


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


class FilterOutTranslationese(object):
    """Get proceedings of the European Parliament."""

    @timeit
    def __init__(self):
        self.langs = {
            "bg",
            "es",
            "cs",
            "da",
            "de",
            "et",
            "el",
            "en",
            "fr",
            "ga",
            "hr",
            "it",
            "lv",
            "lt",
            "hu",
            "mt",
            "nl",
            "pl",
            "pt",
            "ro",
            "sk",
            "sl",
            "fi",
            "sv",
            }
        self.nationalities = {
            "bg": ['Bulgaria'],
            "es": ['Spain'],
            "cs": ['Czech Republic', 'Slovakia'],
            "da": ['Denmark'],
            "de": ['Germany', 'Austria', 'Belgium', 'Luxembourg', 'Italy'],
            "et": ['Estonia'],
            "el": ['Greece'],
            "en": ['United Kingdom', 'Ireland', 'Malta'],
            "fr": ['France', 'Belgium', 'Luxembourg', 'Italy'],
            "ga": ['Ireland', 'United Kingdom'],
            "hr": ['Croatia'],
            "it": ['Italy', 'Croatia', 'Slovenia'],
            "lv": ['Latvia'],
            "lt": ['Lituania'],
            "hu": ['Hungary'],
            "mt": ['Malta'],
            "nl": ['Netherlands'],
            "pl": ['Poland'],
            "pt": ['Portugal'],
            "ro": ['Romania'],
            "sk": ['Slovakia', 'Czech Republic'],
            "sl": ['Slovenia'],
            "fi": ['Finland'],
            "sv": ['Sweden', 'Finland'],
            }
        self.cli()
        self.infiles = self.get_files(self.indir, self.pattern)
        self.n_proceedings = 0
        self.main()

    def __str__(self):
        message = "{} EuroParl's {} proceedings filtered!".format(
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

    def read_xml(self, infile):
        """Parse a XML file.

        Keyword arguments:
        infile -- a string for the path to the file to be read.
        """
        parser = etree.XMLParser(remove_blank_text=True)
        with open(infile, encoding='utf-8', mode='r') as input:
            return etree.parse(input, parser)

    def serialize(self, infile, root):
        """Serialize Element as XML file.

        Keyword arguments:
        infile -- a string for the path to the input file processed.
        root -- Element to be serialized as XML.
        """
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

    def get_langs_to_be_removed(self):
        langs_to_be_removed = {'unknown'}
        if self.sl != 'all' and self.sl == self.language:  # originals
            langs_to_be_removed.update(self.langs.difference({self.sl}))
        elif self.sl != 'all' and self.sl != self.language:  # translations_SL
            langs_to_be_removed.update({self.language})
            langs_to_be_removed.update(self.langs.difference({self.sl}))
        elif self.sl == 'all':  # translations_all
            langs_to_be_removed.update({self.language})
        return langs_to_be_removed

    def remove_element(self, element):
        parent = element.getparent()
        parent.remove(element)
        if len(parent) == 0:
            parent.getparent().remove(parent)
        pass

    def main(self):
        for infile in self.infiles:
            print(infile)
            tree = self.read_xml(infile)
            root = tree.getroot()
            self.language = root.attrib['lang']
            self.langs_to_be_removed = self.get_langs_to_be_removed()
            print(self.langs_to_be_removed)
            elements = tree.xpath('//{}'.format(self.element))
            for e in elements:
                if self.native is False:
                    if e.attrib['sl'].lower() in self.langs_to_be_removed:
                        self.remove_element(e)
                else:
                    if self.sl != 'all':
                        if (e.attrib['sl'].lower() in self.langs_to_be_removed
                                or (e.attrib['sl'] == self.sl
                                    and e.getparent().attrib['nationality']
                                    not in self.nationalities[self.sl])):
                            self.remove_element(e)
                    else:
                        if e.attrib['sl'].lower() in self.langs_to_be_removed:
                            self.remove_element(e)
                        elif 'nationality' in e.getparent().attrib:
                            if (e.getparent().attrib['nationality'] not in
                                    self.nationalities[e.attrib['sl'].lower()]):
                                self.remove_element(e)
            self.serialize(infile, root)
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
            "-o", "--output",  # originals
            required=True,
            help="path to the output directory.")
        parser.add_argument(
            "-l", "--language",
            required=True,
            choices=list(self.langs)+['all'],
            help="source language(s).")
        parser.add_argument(
            "-n", "--native",
            required=False,
            default=False,
            action="store_true",
            help="filter out speeches by non-native speakers.")
        parser.add_argument(
            '-p', "--pattern",
            required=False,
            default="*.xml",
            help="glob pattern to filter files.")
        parser.add_argument(
            '-e', "--element",
            required=False,
            default='p',
            help="Element containing the language attribute.")
        args = parser.parse_args()
        self.indir = args.input
        self.outdir = args.output
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        self.sl = args.language
        self.pattern = args.pattern
        self.element = args.element
        self.native = args.native
        pass


print(FilterOutTranslationese())
