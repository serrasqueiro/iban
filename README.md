# iban

IBAN on SEPA:
- git sources:
  + https://github.com/serrasqueiro/iban/

## Quick How-To

- `python3 nibs.py ./eea/tables/pt_NIBS.xlsx 2`
  + it generates `iban-pt.json` json output.

## Sources

- `sources/iban-pt.txt` - Portugal
  + Generated from [anchor_iban_pt_nib] ([1])
- `sources/iban-de.txt` - Deutschland (Germany)
  + See also [www.iban.com/country/germany/](https://www.iban.com/country/germany/)

- `eea/`
  + eea ([European Economic Area](https://en.wikipedia.org/wiki/European_Economic_Area)) submodule is not public; it holds [LibreOffice] ([2]) xlsx files with country NIBs.
  + This is designated *NIBS.xlsx*

The workflow is as follow:
1. Banking supervisory authority publishes or updates NIB (**B**anking **I**dentification **N**umber)
1. eea repository is reliably updated accordingly. *NIBS.xlsx* is updated:
old or disbanded NIBs are marked with a date on the first column (_Expired_).
1. _sources/iban-$$.txt_ is updated,
   + here: https://github.com/serrasqueiro/iban/blob/master/sources/
   + example: sources/iban-**pt**.txt

# Scripts

- `nibs.py` - lists NIBs (pairs) from [LibreOffice] ([2]) (xlsx) file
  + xlsx file should have 3 columns: 'Expired'; 'Code'; 'Name'
  + currently this script only handles _**pt**_ Country Code; see also [country_code] ([3])

# References

[1]: https://gist.github.com/serrasqueiro/ed970d4306d6e824d29a9e9e136be654 "anchor_iban_pt_nib"

* [1] - gist [iban_pt_nib]
  + `git@gist.github.com:ed970d4306d6e824d29a9e9e136be654.git`

[2]: https://www.libreoffice.org/discover/libreoffice/ "LibreOffice"

* [2] - LibreOffice [LibreOffice]
  + [download here](https://www.libreoffice.org/download/)

[3]: https://www.iban.com/country-codes "country_code"

* [3] - Country Code
  + ISO standard ([here](https://www.iso.org/iso-3166-country-codes.html)): ISO 3166-1 alpha-2
