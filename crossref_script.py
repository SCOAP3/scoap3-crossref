import csv
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_nested_field(json_obj, field_path):
    keys = field_path.split(".")

    def recurse(obj, key_idx, path_parts):
        if key_idx == len(keys):
            yield ".".join(path_parts), obj
            return

        key = keys[key_idx]

        if isinstance(obj, dict):
            if key in obj:
                yield from recurse(obj[key], key_idx + 1, path_parts + [key])
            else:
                yield ".".join(path_parts + [key]), None

        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if path_parts:
                    indexed = path_parts[:-1] + [f"{path_parts[-1]}[{i}]"]
                else:
                    indexed = [f"[{i}]"]
                yield from recurse(item, key_idx, indexed)

        else:
            yield ".".join(path_parts + [key]), None

    initial = keys[0]
    if isinstance(json_obj, dict) and initial in json_obj:
        yield from recurse(json_obj[initial], 1, [initial])
    else:
        yield field_path, None

def fetch_work_by_doi(doi):
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return doi, response.json().get("message", {})
    except requests.RequestException as e:
        print(f"An error occurred for DOI {doi}: {e}")
        return doi, None

def fetch_all_works_concurrently(dois):
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_doi = {executor.submit(fetch_work_by_doi, doi): doi for doi in dois}
        for future in as_completed(future_to_doi):
            yield future.result()

def analyze_fields(json_data, field_analysis):
    for field, analysis_type in field_analysis.items():
        results = list(get_nested_field(json_data, field))

        if analysis_type == "y/n":
            for path, value in results:
                yield path, "y" if value else "n"
        elif analysis_type == "nr":
            count = sum(1 for _, value in results if value is not None)
            yield field, f"nr: {count}"
        elif analysis_type == "data":
            for path, value in results:
                yield path, value

def write_to_csv(dois, field_analysis, filename="output.csv"):
    all_rows = []
    all_fieldnames = set()

    for doi, json_data in fetch_all_works_concurrently(dois):
        if json_data:
            row = {"article": doi}
            analysis_results = dict(analyze_fields(json_data, field_analysis))
            row.update(analysis_results)
            all_fieldnames.update(analysis_results.keys())
            all_rows.append(row)

    if not all_rows:
        print("No data to write.")
        return

    sorted_fieldnames = ["article"] + sorted(list(all_fieldnames))

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=sorted_fieldnames)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)

    print(f"Data has been written to '{filename}'")

def read_dois_from_csv(filename):
    dois = []
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if "doi" not in reader.fieldnames:
                raise ValueError("CSV file must contain a 'doi' column")
            for row in reader:
                if row.get("doi"):
                    dois.append(row["doi"])
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return dois


# Script Parameters:
field_analysis = {
    "accepted.date-parts": "y/n",
    "author.given": "nr",
    "author.family": "nr",
    "author.sequence": "nr",
    "author.ORCID": "nr",
    "author.authenticated-orcid": "nr",
    "DOI": "y/n",
    "author.affiliation.name": "nr",
    "author.affiliation.id.id": "nr",
    "container-title": "y/n",
    "ISSN": "y/n",
    "volume_year": "y/n",
    "issue": "y/n",
    "issue_date": "y/n",
    "volume": "y/n",
    "title": "y/n",
    "article-number": "y/n",
    "alternative-id": "y/n",
    "relation.has-preprint.id": "y/n",
    "relation.has-preprint.id-type": "y/n",
    "page": "data",
    "abstract": "y/n",
    "funder.award": "nr",
    "funder.DOI": "nr",
    "funder.name": "nr",
    "assertion.value": "data",
}

input_file = "dois.csv"
dois_to_process = read_dois_from_csv(input_file)

if dois_to_process:
    write_to_csv(dois_to_process, field_analysis, "output.csv")