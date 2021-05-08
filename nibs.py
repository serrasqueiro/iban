#-*- coding: utf-8 -*-
# nibs.py  (c)2020  Henrique Moreira

"""
Displays NIBs from Excel file

Uses 'xcelent', openpyxl wrapper
"""

# pylint: disable=missing-function-docstring

import sys
import openpyxl
import filing.xcelent as xcelent
import waxpage.redit as redit


def main():
    """ Main script """
    main_test(sys.argv[1:])

def main_test(args):
    dump_nibs(args[0])

def dump_nibs(fname) -> int:
    """ Input should be an OpenLibre xls(x) file """
    wbk = openpyxl.load_workbook(fname)
    #booklet = xcelent.dict_from_sheets(wbk)
    libre = xcelent.Xcel(wbk, "nibs")
    sheet = libre.get_sheet("pt")
    items = [(row[1].value, row[2].value) for row in sheet.rows if row[0].value is None]
    for num, text in items:
        if text is None:
            continue
        s_text = redit.char_map.simpler_ascii(text)
        try:
            anum = int(num)
        except ValueError:
            print("# Invalid code:", num, s_text)
            anum = None
        if anum is None:
            continue
        print(f"{anum}\t{s_text}")
    return 0


# Main script
if __name__ == "__main__":
    main()
