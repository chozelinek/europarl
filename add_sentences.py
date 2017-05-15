# -*- coding: utf-8 -*-

import os
import argparse
from lxml import etree
import fnmatch
import time
import json
import nltk


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


class AddSentences(object):
    """Split text in sentences."""

    @timeit
    def __init__(self):
        self.cli()
        self.infiles = self.get_files(self.indir, self.pattern)
        self.n_proceedings = 0
        self.loc = self.get_localized_vars()
        self.tokenizer = self.init_tokenizer()
        self.main()

    def __str__(self):
        message = "{} EuroParl's {} proceedings processed!".format(
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

    def get_localized_vars(self):
        """Import localized variables from JSON file."""
        fname = self.language+".json"
        fpath = os.path.join('localization', fname)
        with open(fpath, mode="r", encoding="utf-8") as jfile:
            content = jfile.read()
        vars = json.loads(content)
        return vars

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

    def init_tokenizer(self):
        """Instantiate a tokenizer suitable for the language at stake."""
        lang = {'en': 'english', 'de': 'german', 'es': 'spanish'}
        tokenizer = nltk.data.load(
            'tokenizers/punkt/{}.pickle'.format(lang[self.language]))
        if 'extra_abbreviations' in self.loc:
            tokenizer._params.abbrev_types.update(
                self.loc['extra_abbreviations'])
        return tokenizer

    def get_sentences(self, element):
        """Split element's text in sentences.

        Keyword arguments:
        element -- Element whose text has to be split.
        """
        text = element.text
        sentences = self.tokenizer.tokenize(text)
        element.text = None
        for sentence in sentences:
            etree.SubElement(element, 's').text = sentence
        pass

    def main(self):
        for infile in self.infiles:
            print(infile)
            tree = self.read_xml(infile)
            elements = tree.xpath('.//{}'.format(self.element))
            for e in elements:
                self.get_sentences(e)
            self.serialize(infile, tree)
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
            "-l", "--language",
            required=True,
            choices=['en', 'es', 'de'],
            help="language of the version to be processed.")
        parser.add_argument(
            "-e", "--element",
            required=False,
            default='p',
            help="XML element containing the text to be split in sentences.")
        parser.add_argument(
            '-p', "--pattern",
            required=False,
            default="*.xml",
            help="glob pattern to filter files.")
        args = parser.parse_args()
        self.indir = args.input
        self.outdir = args.output
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        self.language = args.language
        self.element = args.element
        self.pattern = args.pattern
        pass


print(AddSentences())
