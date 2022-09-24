#-*- coding: utf-8 -*-
# dump_listaiban.py  (c)2022  Henrique Moreira

""" Dumps textual listaiban.xlsx
"""

# pylint: disable=missing-function-docstring

import sys
import unidecode
import openpyxl
import filing.xcelent

DEF_ENCODING = "ISO-8859-1"
DEF_INPUT_XLSX = "bptables/tables-pt/listaiban.xlsx"
DEF_OUTPUT = "sources/listaiban.tsv"


def main():
    """ Main script """
    code = main_run(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print(f"""Usage:

{__file__} [options] xlsx-file

Use dot ('.') or {DEF_INPUT_XLSX}

Options:
	-v	Verbose
""")
    sys.exit(code if code else 0)


def main_run(out, err, args):
    assert out
    verbose = 0
    if not args:
        return None
    param = args
    if param[0] == "-v":
        verbose += 1
        del param[0]
    if not param:
        return None
    if len(param) > 1:
        return None
    in_file = param[0]
    in_file = in_file if in_file != "." else DEF_INPUT_XLSX
    if verbose > 0:
        print(f"Reading {in_file}")
    debug = verbose
    astr, cont = read_listaiban(in_file, debug=debug)
    if astr:
        print("Uops:", astr)
        err.write(str + "\n")
        return 1
    output_texts(DEF_OUTPUT, cont)
    return 0

def output_texts(outname, cont:list):
    """ Output content to TSV file (text) output.
    """
    #enc = "utf-8"
    enc = DEF_ENCODING
    with open(outname, "w", encoding=enc) as fdout:
        for idx, line in cont:
            assert idx > 0
            s_line = "\t".join(line)
            #print(":::", idx, simple_ascii(line))
            fdout.write(s_line + "\n")
    return True

def read_listaiban(in_file, debug:int=0) -> tuple:
    """ Reads Libre xlsx file and returns message error.
    """
    # pylint: disable=unnecessary-comprehension
    cont = []
    wbk = openpyxl.load_workbook(in_file)
    libre = filing.xcelent.Xcel(wbk)
    sheet = libre.get_sheet(1)
    rows = [row for row in sheet.rows]
    idx = -1
    for idx, arow in enumerate(rows, 1):
        line = [safe_string(elem.value) for elem in arow]
        there = [0 if item is None else 1 for item in line]
        if debug > 0:
            print(idx, [simple_ascii(item) for item in line])
        if sum(there) != 4:
            break
        skip = 0
        for item in line:
            if item is not None and "\n" in item:
                skip = 1
        if skip:
            continue
        bank = (idx, line)
        cont.append(bank)
    assert idx > 0
    if idx < 178:
        return "Input is too short", None
    return "", cont


def simple_ascii(astr, default="-"):
    """ Returns string without accents
    """
    if astr is None:
        return default
    if isinstance(astr, (tuple, list)):
        return [simple_ascii(elem, default) for elem in astr]
    if isinstance(astr, str):
        return unidecode.unidecode(astr)
    return astr

def safe_string(astr):
    if not isinstance(astr, str):
        return astr
    # Replace En-Dash (U2013)
    #	https://www.fileformat.info/info/unicode/char/2013/index.htm
    return astr.replace("\u2013", "@")


# Main script
if __name__ == "__main__":
    main()
