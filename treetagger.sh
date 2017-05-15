## Script for commands to tag corpus with TreeTagger

## Path to the directory to save corpus data
DATA=../data
IDIR_EN=$DATA/xml_sentence/EN
IDIR_ES=$DATA/xml_sentence/ES
IDIR_DE=$DATA/xml_sentence/DE
ODIR_EN=$DATA/ttg/EN
ODIR_ES=$DATA/ttg/ES
ODIR_DE=$DATA/ttg/DE

## Create output directories
mkdir -p $ODIR_EN
mkdir -p $ODIR_ES
mkdir -p $ODIR_DE

## English
echo "Tagging English proceedings with TreTagger ...."
for i in $IDIR_EN/*.xml; do echo $i; tree-tagger-english < $i > $ODIR_EN/$(basename $i); done
## Spanish
echo "Tagging Spanish proceedings with TreeTagger ...."
for i in $IDIR_ES/*.xml; do echo $i; tree-tagger-spanish < $i > $ODIR_ES/$(basename $i); done
## German
echo "Tagging German proceedings with TreeTagger ...."
for i in $IDIR_DE/*.xml; do echo $i; tree-tagger-german < $i > $ODIR_DE/$(basename $i); done
