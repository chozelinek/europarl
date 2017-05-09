## Compile EuroParl corpus

## Path to the directory to save corpus data
DATA=../data
echo "Compiling EuroParl corpus in '$DATA' ...."

## Download proceedings in HTML
## English
echo "Downloading English proceedings ...."
python get_proceedings.py -o $DATA/html/EN -l EN -d dates.EN.txt
# Spanish
echo "Downloading Spanish proceedings ...."
python get_proceedings.py -o $DATA/html/ES -l ES -d dates.EN.txt
# German
echo "Downloading German proceedings ...."
python get_proceedings.py -o $DATA/html/DE -l DE -d dates.EN.txt

## Download MEPs metadata in HTML
echo "Downloading MEPS' metadata ...."
python get_meps.py -o $DATA/meps

## Get proceedings in TXT
## English
echo "Getting English proceedings in TXT ...."
python proceedings_txt.py -i $DATA/html/EN -o $DATA/txt/EN
## Spanish
echo "Getting Spanish proceedings in TXT ...."
python proceedings_txt.py -i $DATA/html/ES -o $DATA/txt/ES
## German
echo "Getting German proceedings in TXT ...."
python proceedings_txt.py -i $DATA/html/DE -o $DATA/txt/DE

## Get proceedings in XML
## English
echo "Getting English proceedings in XML ...."
python proceedings_xml.py -i $DATA/html/EN -o $DATA/xml/EN/ -l EN
## Spanish
echo "Getting Spanish proceedings in XML ...."
python proceedings_xml.py -i $DATA/html/ES -o $DATA/xml/ES/ -l ES
## German
echo "Getting German proceedings in XML ...."
python proceedings_xml.py -i $DATA/html/DE -o $DATA/xml/DE/ -l DE

## Get MEPs metadata in CSV
echo "Extracting metadata in CSV ...."
python meps_ie.py -i $DATA/html/MEPS/ -o $DATA/metadata/

## Add MEPs metadata to XML proceedings
## English
echo "Adding metadata to English proceedings ...."
python add_metadata.py -m $DATA/metadata/meps.csv -n $DATA/metadata/national_parties.csv -g $DATA/metadata/political_groups.csv -x $DATA/xml/EN/ -p "*.xml" -o $DATA/xml_metadata/EN
## Spanish
echo "Adding metadata to Spanish proceedings ...."
python add_metadata.py -m $DATA/metadata/meps.csv -n $DATA/metadata/national_parties.csv -g $DATA/metadata/political_groups.csv -x $DATA/xml/ES/ -p "*.xml" -o $DATA/xml_metadata/ES
# German
echo "Adding metadata to German proceedings ...."
python add_metadata.py -m $DATA/metadata/meps.csv -n $DATA/metadata/national_parties.csv -g $DATA/metadata/political_groups.csv -x $DATA/xml/DE/ -p "*.xml" -o $DATA/xml_metadata/DE
