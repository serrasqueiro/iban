#-*- coding: utf-8 -*-
# nibs_pt.py  (c)2021  Henrique Moreira

"""
Outputs specific Portuguese 'pt' IBANs (aka NIB)

IBAN: International Bank Account Number (eea)
NIB: Banking Identification Number
"""

# pylint: disable=missing-function-docstring

import sys
import json
import openpyxl
import waxpage.redit as redit

DEF_ENCODING = "ISO-8859-1"
DEF_INPUT_XLSX = "eea/tables/listaiban.xlsx"


def main():
    """ Main script """
    code = main_run(sys.stdout, sys.stderr, sys.argv[1:], "Lista")
    if code is None:
        print(f"""Usage:

{__file__} xlsx-file

Use dot ('.') or {DEF_INPUT_XLSX}
	-> place that file to check
Checks whether iban-pt.json was correctly generated.
""")
    sys.exit(code if code else 0)


def main_run(out, err, args, sheetname:str):
    assert out
    if not args:
        return None
    param = args
    if len(param) > 1:
        return None
    in_file = param[0]
    in_file = in_file if in_file != "." else eea/tables/listaiban.xlsx
    astr = read_bp_lista_iban(in_file, sheetname)
    if astr:
        print("Uops:", astr)
        return 1
    return 0


def read_bp_lista_iban(in_file, sheetname, debug:int=0) -> str:
    """ Reads Libre xlsx file and returns message error.
    Checks: iban-pt.json
    """
    msg = ""
    res = []
    in_encode = "utf-8"
    there = json.loads(open("iban-pt.json", "r", encoding=in_encode).read())
    bank_dict = from_iban(there)
    #print("Debug: there:", there)
    wbk = openpyxl.load_workbook(in_file)
    rows = [[item.value for item in row] for row in wbk[sheetname]]
    idx = 0
    for row in rows:
        idx += 1
        if len(row) < 2:
            break
        first = row[0]
        if not isinstance(first, str):
            break
        if idx <= 1:
            continue
        item = redit.char_map.simpler_ascii(row)
        iban_id = "{:04}".format(int(item[0]))
        print(f"# {idx}, iban_id={iban_id} item: {item}")
        _, agente, name, agent_type = item
        entry = {
            "iban-id": iban_id,
            "name": name,
            "agent": agente,
            "agent-type": agent_type,
        }
        res.append(entry)
    #for key, val in bank_dict["by-agent"].items(): print("##", key, val)

    if debug > 0:
        for entry in res:
            print(":::", entry)
            nib_ref = entry["iban-id"]
            where = bank_dict["by-nib-ref"][nib_ref]
            shown = where if len(where) < 3 else [where[:3] + ["..."]]
            print(f"::: -> match (#{len(where)}):", shown)

    # For each xlsx row, check whether json already has that:
    hit_there = {}
    for agente in bank_dict["by-agent"]:
        hit_there[agente] = []
    missing = []
    for entry in res:
        agente = entry["agent"]
        at_json = bank_dict["by-agent"].get(agente)
        if at_json:
            iban_id, name = at_json
            assert entry["name"] == name, f"Mismatch 'name': {entry}"
            #print("Ok:", entry, "//", at_json)
            assert entry["iban-id"] == iban_id, f"Mismatch 'iban-id' and 'nib-ref' at json: {entry}"
            hit_there[agente].append((entry["iban-id"], name))
        else:
            missing.append(entry)
    if missing:
        msg = f"Missing: {missing}"
    else:
        for iban_id in hit_there:
            a_hit = hit_there[iban_id]
            assert a_hit, f"Missing iban_id at json: {iban_id}"
            if debug > 0:
                print("## (at json)", iban_id, a_hit)
    return msg


def from_iban(alist:list) -> dict:
    """ Returns the following dictionary -->
    """
    ba_dict = {
        "by-nib-ref": {},
        "by-agent": {},
    }
    for item in alist:
        agent, name, nib_ref = item["agent"], item["name"], item["nib-ref"]
        assert agent not in ba_dict["by-agent"], f"Duplicate agent '{agent}', this one: {item}"
        ba_dict["by-agent"][agent] = (nib_ref, name)
        if nib_ref in ba_dict["by-nib-ref"]:
            ba_dict["by-nib-ref"][nib_ref].append((agent, name))
        else:
            ba_dict["by-nib-ref"][nib_ref] = [(agent, name)]
    return ba_dict


# Main script
if __name__ == "__main__":
    main()
