# -*- coding: utf-8 -*-

import os
import argparse
from lxml import etree
import fnmatch
import time
from langdetect import detect_langs
from langdetect.lang_detect_exception import LangDetectException
from langid.langid import LanguageIdentifier, model


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


class FilterOutUnexpectedLanguage(object):
    """Identify language of a given string."""

    @timeit
    def __init__(self):
        self.cli()
        self.infiles = self.get_files(self.indir, self.pattern)
        self.n_proceedings = 0
        self.identifier = LanguageIdentifier.from_modelstring(
            model,
            norm_probs=True)
        self.main()

    def __str__(self):
        message = "{} EuroParl's {} proceedings language-identified!".format(
            str(self.n_proceedings),
            self.expected)
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

    def get_parent(self, element):
        """Get parent of a XML Element."""
        parent = element.getparent()
        text = etree.tostring(parent, method='text', encoding='utf-8').decode()
        return text

    def is_expected(self, element):
        """Test if languge of Element's text is the expected language.

        Keyword arguments:
        element -- Element whose text is to be analyzed.
        """
        text = etree.tostring(
            element,
            method='text',
            encoding='utf-8').decode()
        try:
            ld = detect_langs(text)
        except LangDetectException:
            if element.getparent().tag == 'intervention':
                text = self.get_parent(element)
                ld = detect_langs(text)
            else:
                output = None
                return output
        li = self.identifier.classify(text)
        if (li[0] == ld[0].lang) and (li[0] == self.expected):
            output = True
        elif (li[0] != self.expected and li[1] == 1) and li[0] == ld[0].lang:
            output = False
        elif (li[0] != self.expected and li[1] > 0.99) and li[0] == ld[0].lang:
            output = False
        elif li[0] == self.expected and self.expected in [x.lang for x in ld]:
            output = True
        elif (li[0] == self.expected and self.expected not in
                [x.lang for x in ld]):
            output = True
        elif (li[0] != self.expected and li[1] == 1) and li[0] != ld[0].lang:
            output = False
        elif ((li[0] != self.expected and li[1] < 0.9) and
                ld[0].lang == self.expected):
            output = True
        else:
            output = None
        if output is None:
            if element.getparent().tag == 'intervention':
                output = self.is_expected(element.getparent())
            else:
                output = None
        return output

    def main(self):
        for infile in self.infiles:
            print(infile)
            tree = self.read_xml(infile)
            root = tree.getroot()
            self.expected = root.attrib['lang']
            elements = tree.xpath('//{}'.format(self.text))
            for e in elements:
                is_expected = self.is_expected(e)
                if is_expected is False or is_expected is None:
                    parent = e.getparent()
                    parent.remove(e)
                    if len(parent) == 0:
                        parent.getparent().remove(parent)
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
            "-t", "--text",
            required=False,
            default="p",
            help="name of the XML element containing the text to be analyzed.\
            Default: 'p'.")
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
        self.pattern = args.pattern
        self.text = args.text
        self.pattern = args.pattern
        pass


print(FilterOutUnexpectedLanguage())
