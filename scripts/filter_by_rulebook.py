import csv
import os

from csv_commons import dialect
from csv_commons import encoding


csvdir = '../'
books_file = 'books.csv'
id_header = 'id'
rulebook_fk_header = 'rulebook_id'
outdir = csvdir + 'filtered/'
book_selection = [
    '6',   # player's handbook
    '61',  # complete warrior
    '55',  # complete arcane
    '54',  # complete adventurer
    '56'   # complete divine
]


def has_rulebook_header(filename):
    filepath = os.path.join(csvdir, filename)
    with open(filepath, 'r', encoding=encoding) as file:
        reader = csv.DictReader(file, dialect=dialect)
        headers = reader.fieldnames
        return rulebook_fk_header in headers


def get_files_with_rulebook():
    for root, dirnames, filenames in os.walk(csvdir):
        files_with_rulebook = filter(has_rulebook_header, filenames)
        return list(files_with_rulebook)


def init_file(filepath):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    infilepath = csvdir + filepath
    outfilepath = outdir + filepath
    return infilepath, outfilepath


def init_filtering(infile, outfile):
    reader = csv.DictReader(infile, dialect=dialect)
    headers = reader.fieldnames
    writer = csv.DictWriter(outfile, headers, dialect=dialect)
    writer.writeheader()
    return reader, writer


def filter_file_rows(reader, writer, rulebook_header):
    for row in reader:
        book_id = row[rulebook_header]
        if book_id in book_selection:
            writer.writerow(row)


def filter_file(filename, rulebook_header):
    infilepath, outfilepath = init_file(filename)
    with open(infilepath, 'r', encoding=encoding) as infile, open(outfilepath, 'w+', encoding=encoding) as outfile:
        reader, writer = init_filtering(infile, outfile)
        filter_file_rows(reader, writer, rulebook_header)
    print(filename)


def filter_rule_files():
    for filename in get_files_with_rulebook():
        filter_file(filename, rulebook_fk_header)

def filter_book_file():
    filter_file(books_file, id_header)


filter_book_file()
filter_rule_files()
