# Library holdings coverage of SJR titles

## What is this?
This repository includes code that will compare list(s) of journal titles from [Scimago Journal Ranking reports (SJR)](https://www.scimagojr.com/journalrank.php) against your library's holdings of journals in Primo. It will generate a spreadsheet of the full-text availability for all titles in the report, automatically, so that you don't have to check titles one-by-one! This notebook will work with libraries that use Alma and Primo.

The repository contains a few files of code, but it is designed to be operated from a Jupyter Notebook, which includes step-by-step instructions for setup, preparation, and the analysis.

### Example
Want to have a look at what the output looks like? Head to the `results` folder and look inside the `example results` folder. This spreadsheet was generated in less than 1 minute, and shows which journals we have access to and which ones we don't!

## How does it work
In essence, the notebook works by:
* Grabbing the ISSNs from a single, or several, CSV exports from the Scimago Journal Rankings website
* Takes the ISSN and queries the Alma Link resolver
* Takes the XML response and parses out the coverage statements, if any
* Interprets the coverage statements and turns it into a simple availability statement for each title:
   * Full-text available to present
   * Full-text available with embargo
   * Full-text available, but not complete
   * No full-text available

## What is this useful for?
The main use case is to provide insight on scholarly journal holdings for university program reviews. You can quickly see how many of the top-rated journals you have in your collection, and either provide a summary stat on that, or provide a full listing title-by-title.

## Notes & disclaimer
This code may not be perfect, so it is worth double checking the results. Errors will also be introduced based on the metadata quality:

* The ISSNs provided by the SJR report may not match up with the ISSNs in your MARC records
* The coverage availability statements are pulled from the link resolver, which are only as good as your electronic records in Alma

I am always welcome to collaboration -- if this work can be improved, please reach out!
