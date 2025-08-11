# SCOAP3 CrossRef DOI Analysis Script

A Python script that fetches publication metadata from CrossRef API for a list of DOIs and exports the data to CSV.

## What You Need

- Python 3.6+
- `requests` library: `pip install requests`

## How to Run

1. **Have a DOI list in CSV** - You can either use the CSV results from SCOAP3's `year_export` or make your own CSV file with this format, all that matters is that you have a column named `doi` and you name the file `dois.csv` (or change the input file name):
   ```csv
   doi
   10.1103/xgkt-1qsb
   10.1103/bm4l-4mmv
   10.1103/xgkt-1qsb
   ...
   ```
2. Place `dois.csv` in the same directory as `crossref_script.py`

3. **Run the script:**
   ```bash
   python crossref_script.py
   ```

3. **Get your results** - The script creates `output.csv` with the analyzed data.

## How to Customize

### Change which fields to analyze
Edit the `field_analysis` dictionary in the script:

```python
field_analysis = {
    "title": "y/n",           # Check if title exists
    "author.given": "nr",     # Count author given names  
    "page": "data",           # Get actual page numbers
    ...
}
```

### Analysis types:
- `"y/n"` - Returns "y" if field exists, "n" if not
- `"nr"` - Counts how many times field appears
- `"data"` - Returns the actual field values

### Change input/output files
Edit these lines in the script:
```python
input_file = "dois.csv"           # Your DOI list
write_to_csv(dois, field_analysis, "output.csv")  # Your output file
```
