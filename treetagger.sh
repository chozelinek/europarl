## Script for commands to tag corpus with TreeTagger
echo "Compiling EuroParl corpus in '$DATA' ...."

## Path to the directory to save corpus data
DATA=../data
IDIR_EN=$DATA/xml_metadata/EN
IDIR_ES=$DATA/xml_metadata/ES
IDIR_DE=$DATA/xml_metadata/DE
ODIR_EN=$DATA/treetagger/EN
ODIR_ES=$DATA/treetagger/ES
ODIR_DE=$DATA/treetagger/DE

## Create output directories
mkdir -p $ODIR_EN
mkdir -p $ODIR_ES
mkdir -p $ODIR_DE

## English
echo "Tagging English proceedings ...."
for i in $IDIR_EN/*.xml; do echo $i; tree-tagger-english < $i > $ODIR_EN/$(basename $i); done
## Spanish
echo "Tagging Spanish proceedings ...."
for i in $IDIR_ES/*.xml; do echo $i; tree-tagger-spanish < $i > $ODIR_ES/$(basename $i); done
## German
echo "Tagging German proceedings ...."
for i in $IDIR_DE/*.xml; do echo $i; tree-tagger-german < $i > $ODIR_DE/$(basename $i); done
