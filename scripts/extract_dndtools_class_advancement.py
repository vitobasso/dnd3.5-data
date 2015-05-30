'''
Reads class advancement tables from the dndtools database to generate class.csv and class_traits.csv
The source csv is obtained by
    1. obtain dndtools sqlite dump from the links in "references"
    2. sql select for classes in "dndtools.sql"
    3. export as csv
'''

import csv
import re

cleanRegex = r'_\\.*|^"? *\| *| *\| *"?$| *-- *(?=\|)|_\. *|(?<=\d)st (?=\|)|(?<=\d)nd (?=\|)|(?<=\d)rd (?=\|)|(?<=\d)th (?=\|)|(?<=\|) \+|(/\+\d*)+ *|(?<=\|) *| *(?=\|)' #133
# cleanRegex = r'_\\.*|^"? *\| *| *\| *_?\.?"?$| *-- *(?=\|)|_\. *|(?<=\d)st (?=\|)|(?<=\d)nd (?=\|)|(?<=\d)rd (?=\|)|(?<=\d)th (?=\|)|(?<=\|) \+|(/\+\d*)+ *|(?<=\|) *| *(?=\|)' #133
# cleanRegex = r'^"? *\| *| *\| *"?$| *-- *(?=\|)|_\. *|(?<=\d)st *(?=\|)|(?<=\d)nd *(?=\|)|(?<=\d)rd *(?=\|)|(?<=\d)th *(?=\|)|(?<=\|) \+|(/\+\d*)+ *|(?<=\|) *| *(?=\|)|_\\.*$' #133
# cleanRegex = r'_\\.*|^"? *\| *| *\| *_?\.?"?$| *-- *(?=\|)|_\. *|_/\d\. *|(?<=\d)st *(?=\|)|(?<=\d)nd *(?=\|)|(?<=\d)rd *(?=\|)|(?<=\d)th *(?=\|)|(?<=\|) *\+|(/\+\d*)+ *|(?<=\|) *| *(?=\|)' #133

babMap = [None, 'POOR', 'AVERAGE', 'GOOD']
resistMap = ['POOR', None, 'GOOD']
trait_count = 0

class ClassAdv:
    def __init__(self):
        self.bab = None
        self.fort = None
        self.refl = None
        self.will = None
        self.traits = [None] * 20


def cleanTable(tableStr):
    pattern = re.compile(cleanRegex, re.MULTILINE)
    result = pattern.sub('', tableStr)

    result = result.splitlines()
    isNotBlankLine = lambda x: not re.match(r'^\s*$', x)
    result = filter(isNotBlankLine, result)
    return list(result)


def readAdvancementRow(row, classAdv):
    level = int(row['Level'])
    if level == 1:
        classAdv.fort = resistMap[int(row['Fort'])]
        classAdv.refl = resistMap[int(row['Ref'])]
        classAdv.will = resistMap[int(row['Will'])]
    if level == 3:
        classAdv.bab = babMap[int(row['BAB'])]
    if 'Special' in row:
        traitStr = row['Special']
        traitList = re.split(r', *', traitStr)
        classAdv.traits[level - 1] = traitList


def readAdvanementTable(tableLines):
    advModel = ClassAdv()
    reader = csv.DictReader(tableLines, delimiter='|', quoting=csv.QUOTE_NONE)
    failCount = 0
    for row in reader:
        try:
            readAdvancementRow(row, advModel)
        except Exception as e:
            failCount += 1
            #print('Bad row: ', row)

    return advModel, failCount


def readRow(row):
    advStr = row['advancement']
    advLines = cleanTable(advStr)
    result, fails = readAdvanementTable(advLines)
    if fails > 1:
        print(row['id'], row['name'], 'fails:', fails)
    return result, fails


def createClassHeaders(oldHeaders):
    newHeaders = oldHeaders[:]
    pos = newHeaders.index('advancement')
    newHeaders[pos:pos] = ['bab', 'fort', 'refl', 'will']
    newHeaders.remove('advancement')
    newHeaders.remove('class_features')
    newHeaders.remove('requirements')
    return newHeaders


def createClassWriter(outf, oldHeaders):
    newHeaders = createClassHeaders(oldHeaders)
    writer = csv.DictWriter(outf, newHeaders, delimiter=';', quotechar='"', lineterminator='\n')
    writer.writeheader()
    return writer


def writeClassRow(writer, row, model):
    newRow = dict(row, bab=model.bab, fort=model.fort, refl=model.refl, will=model.will)
    newRow.pop('advancement') # remove data already parsed
    newRow.pop('class_features') # remove large, unused data
    newRow.pop('requirements') # remove large, unused data
    writer.writerow(newRow)


def createTraitsWriter(outf):
    headers = ['id', 'rulebook_id', 'class_id', 'level', 'name']
    writer = csv.DictWriter(outf, headers, delimiter=';', quotechar='"', lineterminator='\n')
    writer.writeheader()
    return writer


def writeTraitRow(writer, row, level, name):
    global trait_count
    traitCount += 1 #TODO override: regex pegando o nome repetido com +X
    row = dict(id=traitCount, rulebook_id=row['rulebook_id'], class_id=row['id'], level=level, name=name)
    writer.writerow(row)


def writeClassTraitsForRow(writer, row, model):
    for i, traitList in enumerate(model.traits):
        level = i + 1
        if not traitList:
            continue
        for trait in traitList:
            if not trait:
                continue
            writeTraitRow(writer, row, level, trait)


def countFails(failCount, rowFails):
    if rowFails > 1:
        failCount['manyLines'] += 1
    elif rowFails > 0:
        failCount['oneLine'] += 1


def convertCsv(inFile, classFile, traitFile):
    with open(inFile, 'r') as inf, open(classFile, 'w') as classf, open(traitFile, 'w') as traitf:
        reader = csv.DictReader(inf, delimiter=';', quotechar='"')
        classWriter = createClassWriter(classf, reader.fieldnames)
        traitsWriter = createTraitsWriter(traitf)
        failCount = dict(oneLine=0, manyLines=0)
        for row in reader:
            model, rowFails = readRow(row)
            countFails(failCount, rowFails)
            writeClassRow(classWriter, row, model)
            writeClassTraitsForRow(traitsWriter, row, model)
        print('failed one line:', failCount['oneLine'], 'many lines:', failCount['manyLines'])


in_dir = '../references/csv/'
out_dir = in_dir
in_file = in_dir + 'classes_original.csv'
out_class_file = out_dir + 'classes.csv'
out_traits_file = out_dir + 'class_traits.csv'
convertCsv(in_file, out_class_file, out_traits_file)