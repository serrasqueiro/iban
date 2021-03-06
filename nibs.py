#-*- coding: utf-8 -*-
# nibs.py  (c)2020  Henrique Moreira

"""
Displays NIBs from Excel file

IBAN: International Bank Account Number (eea)
NIB: Banking Identification Number

Uses 'xcelent', openpyxl wrapper
"""

# pylint: disable=missing-function-docstring

import sys
import json
import openpyxl
import filing.xcelent as xcelent
import waxpage.redit as redit

DEF_ENCODING = "ISO-8859-1"

IBAN_N_DIGITS = 34

DEFAULT_LIBRE_PT_NIBS = "eea/tables/pt_NIBS.xlsx"
SOURCE_IBAN_CC = "sources/iban-$$.txt"

SAMPLE_IBAN_DE_UNICEF = "IBAN DE57 3702 0500 0000 3000 00"

NIB_NUM_CC = {
    "@default": 4,
    "pt": 4,
    }

DIGIT_CHECKS_CC = {
    "pt": (0, 25-2, 25-2, 34),
}

CC_IBAN_FORMAT = {
    "@format": "kk: IBAN check digit",
    "pt": "PTkk bbbb ssss cccc cccc ccc.xx",
    "de": "DEkk bbbb bbbb cccc cccc cc",
    "es": "ESkk bbbb ssss xxcc cccc cccc",
    }


def main():
    """ Main script """
    main_test(sys.stdout, sys.stderr, sys.argv[1:])

def main_test(out, err, args) -> int:
    assert out
    default_libre_nibs = DEFAULT_LIBRE_PT_NIBS
    if not args:
        param = [default_libre_nibs]
    else:
        param = args
        if param[0].endswith((".xlsx",)):
            return dump_extra_info(err, param[0], param[1:], "iban-pt.json")
    assert param[0]
    for cc_letters in ("pt",):
        nibs = {
            "0000": "(RESERVED)",
            }
        dump_nibs(param[0], cc_letters, nibs)
        out_name = SOURCE_IBAN_CC.replace("$$", cc_letters)
        is_ok = write_opt_out(cc_letters, out_name, nibs)
        if is_ok:
            print(f"# Written: {out_name}")
        else:
            print(f"# Did not write: {out_name}")
    return 0

def write_opt_out(cc_letters:str, out_name:str, nibs:dict) -> bool:
    num_dig = NIB_NUM_CC.get(cc_letters)
    if num_dig is None:
        num_dig = NIB_NUM_CC["@default"]
    try:
        out = open(out_name, "wb")
    except PermissionError:
        return False
    for nib in sorted(nibs):
        if nib.isdigit() and int(nib) <= 0:
            continue
        shown = nibs[nib]
        assert len(nib) == num_dig, f"Mismatched length (expected: {num_dig}): $nib"
        line = f"{nib}\t{shown}\n"
        out.write(line.encode(DEF_ENCODING))
    return True

def dump_nibs(fname:str, sheet_name:str, nibs:dict) -> int:
    """ Input should be an OpenLibre xls(x) file """
    pattern = sorted(nibs)[0]	# e.g. '0000'
    wbk = openpyxl.load_workbook(fname)
    #booklet = xcelent.dict_from_sheets(wbk)
    libre = xcelent.Xcel(wbk, "nibs")
    sheet = libre.get_sheet(sheet_name)
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
        if pattern == '0000':
            s_num = f"{anum:04}"
        elif pattern.isdigit():
            fmt = "{" + ":0" + str(len(pattern)) + "}"
            s_num = fmt.format(anum)
        else:
            fmt = "{" + ":<" + str(len(pattern)) + "}"
            s_num = fmt.format(anum)
        astr = f"{s_num}\t{s_text}"
        print(astr)
        assert s_num not in nibs, f"Duplicate NIB: {s_num}: {astr}"
        nibs[s_num] = s_text
        nibs[s_num] = s_text
    return 0

def dump_extra_info(err, fname, sheets, outname:str) -> int:
    assert err
    refs = {}
    print("Reading:", fname)
    num_sheets = sheets
    if not sheets:
        num_sheets = [1]
    for num in num_sheets:
        table = dict()
        is_ok = extra_info(fname, int(num), table)
        if not is_ok:
            print(f"Sheet#{num} from {fname}: no such sheet?")
            continue
        tups = table["items"]
        for aline in tups:
            skip = False
            for column in aline:
                if not column:
                    skip = True
                    break
            if skip:
                print(".")
                continue
            triplet = redit.char_map.simpler_ascii(aline)
            bank, nib_ref, name = triplet
            if bank in ("IBAN",):
                err.write(f"# Header: {aline}\n")
                continue
            assert bank not in refs, f"Duplicate nib_ref: {triplet}"
            refs[name] = (bank, nib_ref)
    res = []
    for key in sorted(refs):
        pair1, pair2 = refs[key]
        err.write(f"#	{pair1}.{pair2}: {key}\n")
        item = {
            "name": key,
            "nib-ref": pair1,
            "agent": pair2,	# Agente Financeiro (Banco de Portugal)
        }
        res.append(item)
    astr = json.dumps(res, indent=2, sort_keys=True)
    with open(outname, "w", encoding="ascii") as fdout:
        fdout.write(astr + "\n")
    print("Written:", outname)
    return 0

def extra_info(fname:str, num_sheet, table:dict) -> bool:
    wbk = openpyxl.load_workbook(fname)
    libre = xcelent.Xcel(wbk)
    assert num_sheet >= 1, f"num_sheet >= 1, but it was: {num_sheet}"
    #print("Opening sheet:", fname, num_sheet)
    idx_sheet = num_sheet-1
    try:
        sheet = libre.get_sheet(wbk.sheetnames[idx_sheet])
    except IndexError:
        sheet = None
    if not sheet:
        return False
    rows = [row for row in sheet.rows]
    cont = list()
    for arow in rows:
        these = [elem.value for elem in arow if elem]
        cont.append(these)
    table["items"] = cont
    return True


def samples(dump:bool=True) -> dict:
    """ Dump a couple of IBANs """
    # pylint: disable=line-too-long
    cc_letter_list = (
        "pt",	# Portugal
        "de",	# Germany
        "es",
        )
    urls = {
        "pt": {
            "unicef": (
                "PT50 0033 0000 5013 1901 229 05",
                "https://www.unicef.pt/como-ajudar/outras-formas-de-fazer-o-seu-donativo/",
                ),
            },
        "de": {
            "unicef": (
                "DE57 3702 0500 0000 3000 00",
                "https://www.unicef.de/informieren/ueber-uns/faq/wie-lautet-die-vollstaendige-bankverbindung-mit-iban-und-bic-von-unicef-deutschland-/27870",
                ),
            "wiki": (
                "DE91 1000 0000 0123 4567 89",
                "https://en.wikipedia.org/wiki/International_Bank_Account_Number",
                )
            },
        "es": {
            "unicef": (
                "ES69 2100 5731 77 0200004894",	# Caixabank
                "https://www.unicef.es/colabora/como-donar",
                ),
            },
        }
    result = {"ccs": cc_letter_list, "urls": urls}
    if not dump:
        return result
    for cc_letters in cc_letter_list:
        print("=" * 25, cc_letters, "=" * 25)
        for item in sorted(urls[cc_letters], key=str.casefold):
            there = urls[cc_letters][item]
            s_who = f"{item} @{cc_letters}"
            iban, where = there
            iban = iban.replace(" ", "")
            if cc_letters in DIGIT_CHECKS_CC:
                as_a1, as_a2, as_a3, as_a4 = DIGIT_CHECKS_CC[cc_letters]
                s_iban = iban[as_a1:as_a2] + "." + iban[as_a3:as_a4]
            else:
                s_iban = iban
            gen_fmt = iban_format(cc_letters)
            print(gen_fmt, f"(General format, length={len(gen_fmt)})")
            print(iban)
            print("--")
            print(s_iban, s_who,
                  "\n   ", "URL reference:",
                  where.split("//", maxsplit=1)[-1])
    return result

def iban_format(cc_letters:str):
    """ Returns the IBAN general format """
    astr = CC_IBAN_FORMAT[cc_letters].replace(" ", "").replace(".", "")
    return astr

# Main script
if __name__ == "__main__":
    #samples()
    main()
