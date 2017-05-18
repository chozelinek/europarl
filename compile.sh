## Compile EuroParl corpus

## Usage information
usage() {
    echo "Usage: $0 [-l {en, es, de}] [-p <string>]" 1>&2
    exit 1
}

## List of supported languages
languages=(
    en
    es
    de
)

## language to be processed
LANGUAGE=

## string to filter files
PATTERN=

## check if a value is contained in an array
contains() {
    local list=$1[@]
    local elem=$2
    for i in "${!list}"
    do
        if [ "$i" == "${elem}" ]; then
            return 0
        fi
    done
    return 1
}

## option parser
while getopts hl:p: opt; do
    case $opt in
        l) LANGUAGE=$OPTARG
        ;;
        p) PATTERN=$OPTARG
        ;;
        h) usage
        exit 1
        ;;
        ?) exit 1
        ;;
        :) exit 1
        ;;
    esac
done

## if language provided, check if it is supported, if yes, set languages to it
if [ ! -z "$LANGUAGE" ]; then
    if contains languages "$LANGUAGE"; then
        languages=($LANGUAGE)
    else
        echo "'$LANGUAGE' is not allowed."
        usage
        exit 1
    fi
fi

## Path to the directory to save corpus data
DATA=../data
echo "Compiling EuroParl corpus in '$DATA' ...."

## Download MEPs metadata in HTML
echo "Downloading MEPs' metadata ...."
python get_meps.py -o $DATA/html/meps

## Get MEPs metadata in CSV
echo "Extracting MEPs' metadata in CSV ...."
python meps_ie.py -i $DATA/html/MEPS/ -o $DATA/metadata/

for i in ${languages[@]}
do
    ## Download proceedings in HTML
    echo "Downloading `echo "$i" | tr '[:lower:]' '[:upper:]'` proceedings ...."
    python get_proceedings.py -o $DATA/html/$i -l $i -d dates.txt
    ## Get proceedings in TXT
    echo "Getting `echo "$i" | tr '[:lower:]' '[:upper:]'` proceedings in TXT ...."
    python proceedings_txt.py -i $DATA/html/$i -o $DATA/txt/$i -p "$2*.html"
    ## Get proceedings in XML
    echo "Getting `echo "$i" | tr '[:lower:]' '[:upper:]'` proceedings in XML ...."
    python proceedings_xml.py -i $DATA/html/$i -o $DATA/xml/$i/ -l $i -p "$2*.html"
    xmllint --noout $DATA/xml/$i/$2*.xml
    ## Language ID
    echo "Filtering out text not in `echo "$i" | tr '[:lower:]' '[:upper:]'` ...."
    python langid_filter.py -i ../data/xml/$i -o ../data/xml_langid/$i -p "$2*.xml"
    xmllint --noout $DATA/xml_langid/$i/$2*.xml
    ## Add metadata
    echo "Adding metadata to `echo "$i" | tr '[:lower:]' '[:upper:]'` proceedings ...."
    python add_metadata.py -m $DATA/metadata/meps.csv -n $DATA/metadata/national_parties.csv -g $DATA/metadata/political_groups.csv -x $DATA/xml_langid/$i -o $DATA/xml_metadata/$i -p "$2*.xml"
    xmllint --noout $DATA/xml_metadata/$i/$2*.xml
    ## Split text in sentences
    echo "Splitting sentences for `echo "$i" | tr '[:lower:]' '[:upper:]'` proceedings ...."
    python add_sentences.py -i $DATA/xml_metadata/$i -o $DATA/xml_sentences/$i -l $i -p "$2*"
    xmllint --noout $DATA/xml_sentences/$i/$2*.xml
    ## Tag texts with TreeTagger
    echo "Tagging `echo "$i" | tr '[:lower:]' '[:upper:]'` proceedings with TreeTagger ...."
    python treetagger.py -i $DATA/xml_sentences/$i -o $DATA/xml_ttg/$i -l $i -p "$2*.xml"
    xmllint --noout $DATA/xml_ttg/$i/$2*.xml
    ## Filter originals
    echo "Getting originals in `echo "$i" | tr '[:lower:]' '[:upper:]'` proceedings ...."
    python translationese_filter.py -i $DATA/xml_ttg/$i -o $DATA/xml_translationese/$i/originals -l $i -u -p "$2*.xml"
    xmllint --noout $DATA/xml_translationese/$i/originals/$2*.xml
    ## Filter all translations
    echo "Getting all translations in `echo "$i" | tr '[:lower:]' '[:upper:]'` proceedings ...."
    python translationese_filter.py -i $DATA/xml_ttg/$i/ -o $DATA/xml_translationese/$i/translations_all -l all -u -p "$2*.xml"
    xmllint --noout $DATA/xml_translationese/$i/translations_all/$2*.xml
    ## Filter NS originals
    echo "Getting NS originals in `echo "$i" | tr '[:lower:]' '[:upper:]'` proceedings ...."
    python translationese_filter.py -i $DATA/xml_ttg/$i -o $DATA/xml_translationese/$i/originals_ns -l $i -n -u -p "$2*.xml"
    xmllint --noout $DATA/xml_translationese/$i/originals_ns/$2*.xml
    ## Filter all NS translations
    echo "Getting all NS translations in `echo "$i" | tr '[:lower:]' '[:upper:]'` proceedings ...."
    python translationese_filter.py -i $DATA/xml_ttg/$i -o $DATA/xml_translationese/$i/translations_all_ns -l all -n -u -p "$2*.xml"
    xmllint --noout $DATA/xml_translationese/$i/translations_all_ns/$2*.xml
    if [ "$i" == "es" ]; then
        ## Filter translations from English into Spanish
        echo "Getting translations from English into Spanish ...."
        python translationese_filter.py -i $DATA/xml_ttg/$i -o $DATA/xml_translationese/$i/translations_en -l en -u -p "$2*.xml"
        ## Filter translations from English NS into Spanish
        echo "Getting translations from English NS into Spanish ...."
        python translationese_filter.py -i $DATA/xml_ttg/$i -o $DATA/xml_translationese/$i/translations_en -l en -n -u -p "$2*.xml"
    fi
done
