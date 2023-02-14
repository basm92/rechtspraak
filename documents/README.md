## Guide to trial_small/civil_cases_coded.csv

### State of affairs

This file contains the first trial attempting to extract information from Rechtspraak.nl. 

We set out to look for the following variables:

  - Dossiernummer
  - Namen van de eisende en gedaagde partijen (alleen bij rechtspersonen).
  - Kenmerken partij (wel of niet natuurlijk persoon)
  - Gemachtigde/ geen/ advocaat/ incassobureau/ deurwaarder
  - Financieel belang
  - Toegewezen bedrag
  - Uitspraak van de rechter: de mate waarin de partij die zaak aanspant wordt door de rechter in het gelijk gesteld.
  - **aantal rechters onderin**
  - **naam van de rechters**
  - kort geding dummy variabele

The ones in bold are not yet implemented 
  - But should be easy to implement this 


### Legend of the file trial_small/civil_cases_coded.csv

- First, open the file, and separate the `.csv` by Tabs, not by comma's
  - Because the text data is included and contains comma's, but does not contain tabs. 

- Set the column width to standard width if Excel does not do that automatically for better readability

- Then, the columns and their meaning are as follows:

| Column      | Description |
| ----------- | ----------- |
| index      | URL from court case (1) |
| Datum uitspraak   | Date of result|
| Datum publicatie | Date of publication |
| Rechtsgebied | Area of law |
| Bijzondere kenmerken | Special features (2) |
| Vindplaatsen | Finding place (Rechtspraak.nl) |
| Inhoudsindicatie | Short summary of court case |
| Formele relaties | Formal relations (if applicable) |
| De procedure, De Feiten, Het Geschil, De Beoordeling, De Beslissing | Transcription of the text of the court case |
| lawyers | Names of lawyers, incassobureau or other parties present |
| bedrag | Based on "Geschil". A dictionary of variable length, split up by section in "Geschil": In each element in the dictionary, which money amounts are mentioned in the court case (3) (4)|
| plaintiff | Name(s) of the plaintiff(s) and their representation (lawyer) |
| defendant | Name(s) of the defendant(s) and their representation (lawyer) (5) |
| lose | Based on "Beslissing". A dictionary of length 1 **OR** length 2 (in case of conventie/reconventie). If lenght 1, the dictionary contains dummies for each section, indicating whether the court has mentioned that the party's claims are **rejected**. If length 2, the dictionary contains dummies separately for conventie/reconventie, and then for each section and each conventie/reconventie, whether the claims have been **rejected**. (6) |
| bedrag | Based on "Beslissing". A dictionary of length 1 **OR** length 2 (in case of conventie/reconventie). Similar data structure to bedrag, with a variable length for each unique money amount mentioned in that section. (7) |



#### Notes

1. And identifier to match with the other metadata in trial_small, including Dossiernummer (Case number)
2. Including dummy for "Kort geding"
3. For practical purposes, these numbers can be added together to get a sense of the total amount of money at play in the court case
4. This variable takes into account repeated mentions of money amount by only taking the unique elements
5. These two variabels include the name of the lawyer. With data manipulation, it is easy to filter this out, but I wanted to let this in in order to identify which lawyer belongs to which party. 
6. So the data structure of this variable is as follows: 
	- If conventie/reconventie, the dictionary consists of two elements, attempting to split up the conventie and reconventie part. If not, it constists of one element. 
	- Each of those elements contains a variable number of dummies corresponding to each section in the Conclusion. 
	- Each of those dummies indicate, for each section, whether a string match has been found indicating that the claim in that section is **rejected**. For completeness, the exact string match is reported as a `re.match` object showing the exact match, rather than a 0/1 dummy. 
7. My suggestion would be to consider all money amounts in the sections AFTER a match of a rejection has been found as negative amounts, i.e. amounts the plaintiffs (or reconvener) has to pay because the claims have been rejected. 
