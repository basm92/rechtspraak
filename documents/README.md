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
  - **aantal rechters onderin
	- naam van de rechters**
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
| bedrag | A dictionary of variable length, split up by section in "The Beslissing": In each element in the dictionary, which money amounts are mentioned in the court case (3) (4)|



#### Notes

(1) And identifier to match with the other metadata in trial_small, including Dossiernummer (Case number)
(2) Including dummy for "Kort geding"
(3) For practical purposes, these numbers can be added together to get a sense of the total amount of money at play in the court case
(4) This variable takes into account repeated mentions of money amount by only taking the unique elements
