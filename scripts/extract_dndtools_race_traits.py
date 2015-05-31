'''
Generates race_traits.csv from the dndtools database
The source csv is obtained by
    1. obtain dndtools sqlite dump from the links in "references"
    2. sql select for races in "dndtools.sql"
    3. export as csv
'''

import csv
import re

from csv_commons import dialect
from csv_commons import encoding


in_dir = '../references/csv/'
out_dir = in_dir
in_file = in_dir + 'races_original.csv'
out_file = out_dir + 'race_traits.csv'

clean_regex = r'()|(Ã¯Â¿Â½)'
clean_pattern = re.compile(clean_regex)

find_regex = r'^[\*" ]*(.+?)[:\.]'
find_pattern = re.compile(find_regex, re.MULTILINE)

trait_count = 0


def discard_blanks(result):
    isNotBlankLine = lambda x: not re.match(r'^\s*$', x)
    result = filter(isNotBlankLine, result)
    return list(result)


def find_trait_names(traitsStr):
    matches = find_pattern.finditer(traitsStr)
    result = [m.group(1) for m in matches]
    return result


def extract_traits(traits_str):
    traits_str = clean_pattern.sub('', traits_str)
    result = find_trait_names(traits_str)
    result = discard_blanks(result)
    return result


def read_row(row):
    traitsStr = row['racial_traits']
    return extract_traits(traitsStr)


def writeTraitRow(writer, raceRow, traitName):
    global trait_count
    trait_count += 1
    traitRow = dict(id=trait_count, rulebook_id=raceRow['rulebook_id'], race_id=raceRow['id'], name=traitName)
    writer.writerow(traitRow)


def writeTraitsForRace(writer, raceRow, traits):
    for trait in traits:
        if not trait:
            continue
        writeTraitRow(writer, raceRow, trait)


def createTraitsWriter(outf):
    headers = ['id', 'rulebook_id', 'race_id', 'name']
    writer = csv.DictWriter(outf, headers, dialect=dialect)
    writer.writeheader()
    return writer


def convertCsv(inFile, traitFile):
    with open(inFile, 'r', encoding=encoding) as inf, open(traitFile, 'w+', encoding=encoding) as traitf:
        reader = csv.DictReader(inf, dialect=dialect)
        traitsWriter = createTraitsWriter(traitf)
        for row in reader:
            traits = read_row(row)
            writeTraitsForRace(traitsWriter, row, traits)


convertCsv(in_file, out_file)