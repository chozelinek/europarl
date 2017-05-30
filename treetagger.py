# -*- coding: utf-8 -*-

import os
import argparse
from lxml import etree
import fnmatch
import time
import json
import nltk
import treetaggerwrapper
import html
import re


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


class TagWithTreeTagger(object):
    """Tag text with TreeTagger."""

    @timeit
    def __init__(self):
        self.cli()
        self.infiles = self.get_files(self.indir, self.pattern)
        self.n_proceedings = 0
        self.loc = self.get_localized_vars()
        self.tokenizer = self.init_tokenizer()
        self.tagger = self.init_tagger()
        self.main()

    def __str__(self):
        message = "{} EuroParl's {} proceedings tagged!".format(
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
        
    def unprettify(self, tree):
        """Remove any indentation introduced by pretty print."""
        tree = etree.tostring(  # convert XML tree to string
            tree,
            encoding="utf-8",
            method="xml",
            xml_declaration=True).decode()
        tree = re.sub(  # remove trailing spaces before tag
            r"(\n) +(<)",
            r"\1\2",
            tree)
        tree = re.sub(  # put each XML element in a different line
            r"> *<",
            r">\n<",
            tree)
        tree = re.sub(  # put opening tag and FL output in different lines
            r"(<.+?>)",
            r"\1\n",
            tree)
        tree = re.sub(  # put FL output and closing tag in different liens
            r"(</.+?>)",
            r"\n\1",
            tree)
        tree = re.sub(
            r"(>)([^.])",
            r"\1\n\2",
            tree)
        tree = re.sub(  # remove unnecessary empty lines
            r"\n\n+",
            r"\n",
            tree)
        return tree

    def serialize(self, infile, root):
        """Serialize Element as XML file.

        Keyword arguments:
        infile -- a string for the path to the input file processed.
        root -- Element to be serialized as XML.
        """
        ofile_name = os.path.splitext(os.path.basename(infile))[0]
        ofile_path = os.path.join(self.outdir, ofile_name+'.xml')
        xml = self.unprettify(root)
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
    
    def init_tagger(self):
        tagger = treetaggerwrapper.TreeTagger(TAGLANG=self.language)
        return tagger

    def get_sentences(self, element):
        """Split element's text in sentences.

        Keyword arguments:
        element -- Element whose text has to be split.
        """
        text = element.text
        sentences = self.tokenizer.tokenize(text)
        element.text = None
        return sentences
    
    def escape(self, tags):
        output = []
        for tag in tags:
            if not re.match(r'<', tag):
                output.append(html.escape(tag))
            else:
                test = re.match(r'<rep(.+?) text="(.+)"', tag)
                if test is not None:
                    output.append('<rep{} text="{}" />'.format(test.group(1), html.escape(test.group(2))))
                else:
                    if re.match(r'[<>]\t', tag):
                        output.append(html.escape(tag))
                    else:
                        output.append(tag)
        return output

    def main(self):
        for infile in self.infiles:
            print(infile)
            tree = self.read_xml(infile)
            elements = tree.xpath('.//{}'.format(self.element))
            for e in elements:
                if self.sentence:
                    sentences = self.get_sentences(e)
                    for s in sentences:
                        if self.tokenize:
                            tags = self.tagger.tag_text(html.unescape(s))
                        else:
                            tags = self.tagger.tag_text(html.unescape(s), tagonly=True)
                        etree.SubElement(e, 's').text = '\n'.join(tags)
                else:
                    if self.tokenize:
                        tags = self.tagger.tag_text(html.unescape(etree.tostring(e, encoding='utf-8').decode()))
                    else:
                        tags = self.tagger.tag_text(html.unescape(etree.tostring(e, encoding='utf-8').decode()), tagonly=True)
                    tags = self.escape(tags)   
                    tags = '\n'.join(tags)
                    xml = etree.fromstring(tags)
                    e.getparent().replace(e, xml)
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
        parser.add_argument(
            '-s', "--sentence",
            required=False,
            default=False,
            action="store_true",
            help="if provided, it splits text in sentences.")
        parser.add_argument(
            "--tokenize",
            required=False,
            default=False,
            action="store_true",
            help="if provided, it tokenizes the text, else, it expects one token per line.")
        args = parser.parse_args()
        self.indir = args.input
        self.outdir = args.output
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        self.language = args.language
        self.element = args.element
        self.pattern = args.pattern
        self.sentence = args.sentence
        self.tokenize = args.tokenize
        pass


print(TagWithTreeTagger())
