# -*- coding: utf-8 -*-

import os
import argparse
import datetime
from lxml import etree, html
from lxml.html.clean import Cleaner
import fnmatch  # To match files by pattern
# import regex as re  # Maybe not necessary
import re
import time
import dateparser


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
        self.ns = {'re': 'http://exslt.org/regular-expressions'}
        self.explanations_of_vote = re.compile(r' *EXPLANATIONS? OF VOTES?')
        self.lang_pattern = re.compile(r'.*(BG|ES|CS|DA|DE|ET|EL|EN|FR|GA|HR|IT|LV|LT|HU|MT|NL|PL|PT|RO|SK|SL|FI|SV).*')
        self.lang_pattern_in_text = re.compile(r'\((BG|ES|CS|DA|DE|ET|EL|EN|FR|GA|HR|IT|LV|LT|HU|MT|NL|PL|PT|RO|SK|SL|FI|SV)\)')
        self.roles = {
            'EN': [
                   'Commission',
                   'rapporteur',
                   'Council',
                   'Member of the Commission',
                   'President-in-Office of the Council',
                   'Vice-President of the Commission',
                   '[Aa]uthor',
                   'President of the Commission',
                   'draftsman of the opinion of the Committee on .+',
                   'deputising for the.+?',
                   'Ombudsman',
                   '.*?on behalf of.*?',
                   'President of the .+?',
                   'High Representative for the Common Foreign and Security Policy',
                   'rapporteur for the opinion of the Committee on .+',
                   'Vice-President of the Commission/High Representative of the Union for Foreign Affairs and Security Policy',
                   'President-in-Office of the',
                   'President-in-Office of the Council',
                   'President of the Court of Auditors',
                   'general rapporteur',
                   '[cC]hairman of the Committee on .+?',
                   'deputy rapporteur',
                    ],
            'ES': [
                   'Alto Representante para la Política Exterior y de Seguridad Común',
                   '[aA]utor',
                   '[Cc]omisión',
                   '[Cc]onsejo',
                   'en nombre del .*',
                   '[Mm]iembro de la Comisión.+'
                   '[Pp]onente.+',
                   '[Pp]resident[ea] elect[oa] de la Comisión',
                   '[Pp]resident[ea] designad[oa] de la Comisión',
                   '[Pp]resident[ea] en .+',
                   '[Pp]resident[ea] de.+',
#                    '[Pp]resident[ea] en ejercicio del Consejo',
#                    '[Pp]resident[ea] de la Comisión de .+',
#                    '[Pp]resident[ea] de la Comisión.+',
#                    '[Pp]resident[ea] de la Delegación',
#                    '[Pp]resident[ea] del Banco Central Europeo',
#                    '[Pp]resident[ea] del BCE',
#                    '[Pp]resident[ea] del Tribubal de Cuentas',
#                    '[Pp]resident[ea] de la República.+',
                   '[Vv]icepresident[ea] de la Comisión',
                    ],
            'DE': [
                   'Präsident(in)? de.+',
                   'Kommission',
                   'Rat'
                   ]
                }
        self.president_role_locale = {
            'EN': [
                   'President'
                   ],
            'ES': [
                   'El Presidente',
                   'La Presidenta'
                   ],
            'DE': [
                   '(Der )?Präsident',
                   '(Die )?Präsidentin']
            }
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

    def read_html(self, infile):
        """Parse a HTML file."""
        with open(infile, encoding='utf-8',mode='r') as input:
            return html.parse(input)

    def regextract(self, content, a_pattern, target_dic, dic_attrib):
        """Extract information with a regular expression.

        Keyword arguments:
        a_string -- string
        a_regex -- a string
        target_dic -- a dictionary where the extraction has to be stored
        dic_attrib -- dictionary key where to store extraction
        """
        # match the a_regex in a_string
        is_match = re.match(r'{}'.format(a_pattern), content)
        # if match
        if is_match is not None:
            if dic_attrib not in target_dic.keys():
                target_dic[dic_attrib] = is_match.group(1)
                content = re.sub(r'{}'.format(a_pattern), r'', content)
        return content, target_dic

    def get_speaker_name(self, intervention):
        speaker_name = intervention.xpath('.//span[@class="doc_subtitle_level1_bis"]//text()')
        speaker_name = ''.join(speaker_name)
        speaker_name = re.sub(r'\n', r'', speaker_name)
        speaker_name = re.sub(r' +', r' ', speaker_name)
        speaker_name = re.sub(r'\(.+?\)', r'', speaker_name)
        speaker_name = re.sub(r' +\. *$', r'', speaker_name)
        speaker_name = re.sub(r'(\w{2,}) +\. *$', r'\1', speaker_name)
        speaker_name = re.sub(r'(\w{2,})\. *$', r'\1', speaker_name)
        speaker_name = re.sub(r'(\w{2,}) *\.? *[–—–−-] *$', r'\1', speaker_name)
        speaker_name = re.sub(r'(\w{2,}) \.$', r'\1', speaker_name)
        speaker_name = re.sub(r'(\w{2,})\.$', r'\1', speaker_name)
        speaker_name = re.sub(r'(\w{2,})\. +$', r'\1', speaker_name)
        speaker_name = re.sub(r'(\w{2,})\. $', r'\1', speaker_name)
        speaker_name = re.sub(r', *$', r'', speaker_name)
        speaker_name = re.sub(r', $', r'', speaker_name)
        speaker_name = re.sub(r', . - $', r'', speaker_name)
        speaker_name = re.sub(r', . – $', r'', speaker_name)
        speaker_name = re.sub(r'[  ]+\.$', r'', speaker_name)
        speaker_name = re.sub(r' . –$', r'', speaker_name)
        speaker_name = re.sub(r', – ', r'', speaker_name)
        speaker_name = re.sub(r' , –', r'', speaker_name)
        speaker_name = re.sub(r'(\w{2,})\. –$', r'\1', speaker_name)
        speaker_name = re.sub(r'(\w{2,})\. – $', r'\1', speaker_name)
        speaker_name = re.sub(r' –.', r'', speaker_name)
        speaker_name = re.sub(r'. – –', r'', speaker_name)
        speaker_name = re.sub(r',  – ', r'', speaker_name)
        speaker_name = re.sub(r' . – \(', r'', speaker_name)
        speaker_name = re.sub(r'.–', r'', speaker_name)
        speaker_name = re.sub(r'^(.+?). ­$', r'\1', speaker_name)
        speaker_name = speaker_name.strip()
        return speaker_name

    def get_speaker_id(self, intervention):
        speaker_id = intervention.xpath('.//img[@alt="MPphoto"]')
        speaker_id = speaker_id[0].attrib['src']
        speaker_id = os.path.split(speaker_id)[1]
        speaker_id = os.path.splitext(speaker_id)[0]
        return speaker_id

    def get_is_mep(self, speaker_id):
        if speaker_id is not 'photo_generic':
            output = True
        else:
            output = False
        return output

    def get_mode(self, intervention):
        if self.language == 'EN':
            in_writing = intervention.xpath('.//span[@class="italic"][text()[re:test(.,"in writing?")]]', namespaces=self.ns)
        elif self.language == 'ES':
            in_writing = intervention.xpath('.//span[@class="italic"][text()[re:test(.,"[pP]or escrito")]]', namespaces=self.ns)
        elif self.language == 'DE':
            in_writing = intervention.xpath('.//span[@class="italic"][text()[re:test(.,"schriftlich")]]', namespaces=self.ns)
        if len(in_writing) > 0:
            output = 'written'
            for writing in in_writing:
                writing.drop_tree()
        else:
            output = 'spoken'
        return output

    def get_role(self, intervention):
#         roles_test = intervention.xpath('.//span[@class="italic"][text()[re:test(.,"^[\.\W\s]*({})[\.\W\s]*(\([A-Z][A-Z]\))?[\.\W\s]*$")]]'.format('\w.+?'), namespaces=self.ns)
#         for rt in roles_test:
#             print(html.tostring(rt))
#         roles = intervention.xpath('.//span[@class="italic"][text()[re:test(.,"^[\.\W\s]*({})[\.\W\s]*(\([A-Z][A-Z]\))?[\.\W\s]*$")]]'.format('|'.join(self.roles[self.language])), namespaces=self.ns)
        roles = intervention.xpath('.//span[@class="italic"][text()[re:test(.,"^[\s\-–−\.]*({})[\s\-–−\.]*(\([A-Z][A-Z]\))?[\s\-–−\.]*$")]]'.format('|'.join(self.roles[self.language])), namespaces=self.ns)
        if len(roles) > 0:
            output = roles[0].text.strip()
            for role in roles:
                lang = self.lang_pattern.match(role.text)
                if lang is not None:
                    i_lang = lang.group(1)
                else:
                    i_lang = None
                role.drop_tree()
        else:
            output = None
            i_lang = None
        return output, i_lang

    def get_heading(self, section):
        heading = section.xpath('.//td[@class="doc_title"]//text()')
        heading = ''.join(heading)
        heading = heading.strip()
        heading = re.sub(r'\(\n', r'(', heading)
        heading = re.sub(r'\n,', r',', heading)
        return heading

    def get_language(self, s_intervention, p, i_lang, new_paragraphs):
        language = p.xpath('.//span[@class="italic"][text()[re:test(.,"(BG|ES|CS|DA|DE|ET|EL|EN|FR|GA|HR|IT|LV|LT|HU|MT|NL|PL|PT|RO|SK|SL|FI|SV)")]]', namespaces=self.ns)
        if len(language) > 0 and not self.explanations_of_vote.match(language[0].text):
            lang = self.lang_pattern.match(language[0].text)
            output = lang.group(1)
            for l in language:
                l.drop_tree()
        else:
            p = html.tostring(p, with_tail=True, encoding='utf-8').decode('utf-8')
            lang_in_text = self.lang_pattern_in_text.search(p)
            if lang_in_text is not None:
                output = lang_in_text.group(1)
                p = re.sub(r'\((BG|ES|CS|DA|DE|ET|EL|EN|FR|GA|HR|IT|LV|LT|HU|MT|NL|PL|PT|RO|SK|SL|FI|SV)\) *', r'', p)
            else:
                if len(new_paragraphs) == 0:
                    if 'role' in s_intervention.keys():
                        president_pattern = '|'.join(self.president_role_locale[self.language])
                        if re.match(r'{}'.format(president_pattern), s_intervention['role']):
                            output = 'unknown'
                        else:
                            if i_lang is None:
                                output = self.language
                            else:
                                output = i_lang
                    else:
                        if i_lang is None:
                            output = self.language
                        else:
                            output = i_lang
                else:
                    output = new_paragraphs[-1]['language']
            p = html.fromstring(p)
        return output, p
    
    def clean_paragraph(self, p):
        cleaner = Cleaner(remove_tags=['a'], kill_tags=['sup','img'])
        p = cleaner.clean_html(p)
        doc_subtitle = p.xpath('.//span[@class="doc_subtitle_level1_bis"]')
        for d in doc_subtitle:
            d.drop_tree()
        return p
    

    def get_paragraphs(self, intervention, s_intervention, i_lang):
        paragraphs = intervention.xpath('.//p[@class="contents" or @class="doc_subtitle_level1"]')
        new_paragraphs = []
        for p in paragraphs:
            new_p = {}
            p = html.tostring(p, with_tail=True, encoding='utf-8').decode('utf-8')
            p = re.sub(r'\n+', r' ', p)
            p = re.sub(r'<br ?/?>', r' ', p)
            p = html.fromstring(p)
            p = self.clean_paragraph(p)
            new_p['language'], p = self.get_language(s_intervention, p, i_lang, new_paragraphs)
            content = p.text_content()
            content = content.strip()
            content = re.sub(r'\t', r' ', content)
            content = re.sub(r'\xad', r'-', content)
            content = re.sub(r'\xa0', r' ', content)
            content = re.sub(r' +', r' ', content)
            content = re.sub(r'\. \. \.', r'...', content)
            content = re.sub(r'\.{3,}', r'…', content)
            content = re.sub(r'…\.\.', r'…', content)
            content = re.sub(r'([^\.])(…)', r'\1 \2', content)
            content = re.sub(r'\.…', r' …', content)
            content = re.sub(r'\( ?… ?\)', r'(…)', content)
            content = re.sub(r'(…)(\.)(\w)', r'\1\2 \3', content)
            content = re.sub(r'([\w”])(…)', r'\1 \2', content)
            content = re.sub(r'(…)(\w)', r'\1 \2', content)
            content = re.sub(r'\( +\)', r'', content)
            content = re.sub(r'\( +?', r'(', content)
            content = re.sub(r' +\)', r')', content)
#             content = re.sub(r'^[\s\.–\-−,\)]*\((Madam|Mr President)', r'\1', content)
            content = re.sub(r'^,? *Neil,? +\. +– +', r'', content)
            content = re.sub(r'^\(PPE-DE\), +\. +– +', r'', content)
            content = re.sub(r' +', r' ', content)
            content = re.sub(r'^([\s\.–\-−,\)]+)', r'', content)
            if self.language == 'EN':
                content, s_intervention = self.regextract(content, '^(Member of the Commission)\.[\s\-–]+', s_intervention, 'role')
                content, s_intervention = self.regextract(content, '^(President-elect of the Commission)\.[\s\-–]+', s_intervention, 'role')
                content, s_intervention = self.regextract(content, '^(Commission)\.[\s\-–]+', s_intervention, 'role')
                content, s_intervention = self.regextract(content, '^(Council)\.[\s\-–]+', s_intervention, 'role')
            if self.language == 'ES':
                content, s_intervention = self.regextract(content, '^(Presidente designado de la Comisión)[\s\-–\.]+', s_intervention, 'role')
                content, s_intervention = self.regextract(content, '^(Presidente del Tribunal de Cuentas)[\s\-–\.]+', s_intervention, 'role')
                content, s_intervention = self.regextract(content, '^(Presidente en ejercicio del Consejo)[\s\-–\.]+', s_intervention, 'role')
                content, s_intervention = self.regextract(content, '^(Presidente de la Comisión de Asuntos Económicos y Monetarios)[\s\-–\.]+', s_intervention, 'role')
                
            content = re.sub(r'\*{3,}', r'', content)
            new_p['content'] = content
            new_paragraphs.append(new_p)
        s_intervention['contents'] = new_paragraphs
        return s_intervention

    def add_root_attributes(self, root, tree, infile):
        root.attrib['id'] = os.path.splitext(os.path.basename(infile))[0]
        root.attrib['lang'] = self.language
        date_string = re.match(r'^(.+?,? \d.+?) - (.+)$', tree.xpath('//td[@class="doc_title" and @align="left" and @valign="top"]')[0].text)
        date = dateparser.parse(date_string.group(1)).date()
        place = date_string.group(2)
        root.attrib['date'] = str(date)
        root.attrib['place'] = place
        root.attrib['edition'] = tree.xpath('//td[@class="doc_title" and @align="right" and @valign="top"]')[0].text
        pass

    def intervention_to_xml(self, x_section, s_intervention):
        x_intervention = etree.SubElement(x_section, 'intervention')
        if 'speaker_id' in s_intervention.keys():
            x_intervention.attrib['speaker_id'] = s_intervention['speaker_id']
        if 'name' in s_intervention.keys():
            x_intervention.attrib['name'] = s_intervention['name']
        if 'is_mep' in s_intervention.keys():
            x_intervention.attrib['is_mep'] = str(s_intervention['is_mep'])
        if 'mode' in s_intervention.keys():
            x_intervention.attrib['mode'] = s_intervention['mode']
        if 'role' in s_intervention.keys():
            x_intervention.attrib['role'] = s_intervention['role']
        for paragraph in s_intervention['contents']:
            if len(paragraph['content']) > 0:
                x_p = etree.SubElement(x_intervention, 'p', sl=paragraph['language'])
                x_p.text = paragraph['content']
        pass

    def serialize(self, infile, root):
        ofile_name = os.path.splitext(os.path.basename(infile))[0]
        ofile_path = os.path.join(self.outdir, ofile_name+'.xml')
        xml = etree.tostring(root, encoding='utf-8', xml_declaration=True, pretty_print=True).decode('utf-8')
        with open(ofile_path, mode='w', encoding='utf-8') as ofile:
            ofile.write(xml)
        pass

    def main(self):
        for infile in self.infiles:
            print(infile)
            tree = self.read_html(infile)
            root = etree.Element('text')
            self.add_root_attributes(root, tree, infile)
            sections = tree.xpath('//table[@class="doc_box_header" and @cellpadding="0"]')
            for section in sections:
                heading = self.get_heading(section)
                x_section = etree.SubElement(root, 'section', title=heading)
                interventions = section.xpath('.//table[@cellpadding="5"][.//img[@alt="MPphoto"]]')
                for idx, intervention in enumerate(interventions):
                    s_intervention = {}
                    i_lang = None
                    s_intervention['speaker_id'] = self.get_speaker_id(intervention)
                    s_intervention['is_mep'] = self.get_is_mep(s_intervention['speaker_id'])
                    s_intervention['mode'] = self.get_mode(intervention)
                    speaker_name = self.get_speaker_name(intervention)
                    president_pattern = '|'.join(self.president_role_locale[self.language])
                    if self.language == 'EN':
                        if re.match(r'{}'.format(president_pattern), speaker_name):
                            s_intervention['role'] = 'President'
                        else:
                            s_intervention['name'] = speaker_name
                    elif self.language == 'ES':
                        if re.match(r'{}'.format(president_pattern), speaker_name):
                            s_intervention['role'] = speaker_name
                        else:
                            s_intervention['name'] = speaker_name
                    elif self.language == 'DE':
                        if re.match(r'{}'.format(president_pattern), speaker_name):
                            s_intervention['role'] = speaker_name
                        else:
                            s_intervention['name'] = speaker_name
                    role, i_lang = self.get_role(intervention)
                    if role is not None:
                        s_intervention['role'] = role
                    s_intervention = self.get_paragraphs(intervention, s_intervention, i_lang)
                    self.intervention_to_xml(x_section, s_intervention)
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
            "-o", "--output",
            required=True,
            help="path to the output directory.")
        parser.add_argument(
            "-l", "--language",
            required=True,
            choices=['EN', 'ES', 'DE'],
            help="language of the version to be processed.")
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
        self.pattern = args.pattern
        pass


print(TransformHtmlProceedingsToXml())
