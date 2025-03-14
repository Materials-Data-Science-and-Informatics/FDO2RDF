import argparse
from io import StringIO
import json
import os
import sys
from urllib.parse import urlparse
import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
import requests  # Added requests to handle fetching from URL


def extract_prefixes_from_sssom(sssom_data):
    """
    Extract CURIE prefixes from an SSSOM mapping file.

    The SSSOM file contains a section starting with `#curie_map` that defines
    mappings between CURIE prefixes (short identifiers) and their corresponding full URIs.
    This function scans the file content, extracts these mappings, and returns them as a dictionary.

    Args:
        sssom_data (str): Raw content of the SSSOM file (as a string).

    Returns:
        dict: A dictionary mapping CURIE prefixes to their full URIs.
              Example:
              {
                  "hdo": "http://purl.obolibrary.org/obo/HDO_",
                  "schema": "https://schema.org/"
              }
    """
    curie_map = {}

    if isinstance(sssom_data, dict):
        sssom_data = json.dumps(sssom_data)  # Convert to string if it's a dictionary.

    lines = sssom_data.splitlines()
    in_curie_map_section = False

    for line in lines:
        # print("Processing Line:", line)  # Debugging

        if line.startswith("#curie_map"):
            # print("Found #curie_map section")
            in_curie_map_section = True
            continue

        if line.strip().startswith("#mapping_set_id"):
            # print("End of #curie_map section")
            in_curie_map_section = False

        if in_curie_map_section and ":" in line:
            parts = line.split(":", 1)
            if len(parts) == 2 and line != "#curie_map":
                prefix = parts[0].strip().lstrip("#").lstrip()
                uri = parts[1].strip()
                curie_map[prefix] = uri
                # print(f"Extracted Prefix: {prefix} -> {uri}")  # Debugging

    # print("Final Extracted CURIE Prefixes:", curie_map)
    return curie_map


def get_namespace_for_prefix(prefix, curie_map):
    """
    Retrieve the full namespace (URI) for a given CURIE prefix.

    Args:
        prefix (str): The CURIE prefix (e.g., 'schema', 'dcterms', etc.) that needs to be resolved into a full URI.
        curie_map (dict): A dictionary mapping CURIE prefixes to their full URIs (e.g., {'schema': 'https://schema.org/'})

    Returns:
        str: The corresponding full URI for the given prefix, or an empty string if the prefix is not found.
    """
    return curie_map.get(prefix, "")


def parse_sssom_mapping(sssom_data, curie_map):
    """
    Parses an SSSOM mapping file and returns a dictionary mapping subject_id to object_id.

    Args:
        sssom_data (str): The raw SSSOM data (either from URL or local file content).
        curie_map (dict): Dictionary of CURIE prefixes extracted from the SSSOM file.

    Returns:
        dict: Mapping of subject_id to object_id (RDF predicates).
    """
    print(f"Parsing SSSOM mappings...")

    try:
        mapping = {}
        # Read the CSV from the raw content of the SSSOM file
        sssom_df = pd.read_csv(StringIO(sssom_data), sep="\t", comment="#")

        for _, row in sssom_df.iterrows():
            json_key = row["subject_id"]
            ontology_property = row["object_id"]

            if ":" in json_key:
                prefix, subject_id = json_key.split(":", 1)
                namespace = get_namespace_for_prefix(prefix, curie_map)
                json_key = URIRef(f"{namespace}{subject_id}")
            else:
                json_key = URIRef(json_key).strip()

            if ":" in ontology_property:
                prefix, object_id = ontology_property.split(":", 1)
                namespace = get_namespace_for_prefix(prefix, curie_map)
                ontology_property = URIRef(f"{namespace}{object_id}")
            else:
                ontology_property = URIRef(ontology_property)

            mapping[json_key] = ontology_property

    except Exception as e:
        print(f"Error reading SSSOM mapping: {e}")
        sys.exit(1)

    return mapping


def convert_json_to_rdf(json_data, curie_map, sssom_mappings, output_RDF_file):
    """
    Converts the input JSON data into RDF format using SSSOM mappings and CURIE prefix mappings,
    and writes the resulting RDF data to a Turtle file.

    This function processes the input JSON data and, for each record, uses the provided SSSOM
    mappings to generate the RDF triples. CURIE prefixes are resolved using the curie_map to form
    valid RDF URIs. The resulting RDF graph is serialized to a Turtle format file.

    Args:
        json_data (list): A list of JSON objects, where each object contains the data that
                          needs to be converted to RDF format. Each object is expected to have a
                          'pid' key (the subject) and a 'record' key containing key-value pairs
                          (the predicates and objects) to be added to the RDF graph.

                          Example:
                          [
                              {
                                  "pid": "http://example.org/item/123",
                                  "record": [
                                      {"key": "schema:name", "value": "Example Item"},
                                      {"key": "schema:description", "value": "An example item description"}
                                  ]
                              }
                          ]

        curie_map (dict): A dictionary mapping CURIE prefixes to their full URIs. This is used to
                          resolve CURIEs (e.g., 'schema:name') into full URIs (e.g., 'https://schema.org/name').

                          Example:
                          {
                              "hdo": "http://purl.obolibrary.org/obo/HDO_",
                              "schema": "https://schema.org/"
                          }

        sssom_mappings (dict): A dictionary mapping subject identifiers (as URIs or CURIEs) to their
                               corresponding RDF predicates (object identifiers). This is derived from
                               parsing the SSSOM mapping file.

        output_RDF_file (str): The path to the output Turtle (.ttl) file where the generated RDF data
                               will be saved.

    Returns:
        None: The function does not return any value but writes the resulting RDF data to the
              specified output file.
    """

    if not curie_map:
        print("ERROR: curie_map is EMPTY inside convert_json_to_rdf()!")

    g = Graph()

    # Explicitly bind the 'hdo' prefix to its URI
    for prefix, uri in curie_map.items():
        if prefix == "hdo":
            g.bind("hdo", Namespace(uri))
        else:
            g.bind(prefix, Namespace(uri))

    for obj in json_data:
        pid = obj["pid"]
        pid_uri = URIRef(pid)

        for record in obj["record"]:
            key = record["key"]
            value = record["value"]

            try:
                predicate_uri = sssom_mappings[URIRef(key)]
            except KeyError:
                print(f"** Warning: {key} has no mapping!")
                continue

            predicate = URIRef(predicate_uri)
            # obj = Literal(value)
            if is_valid_url(value):
                obj = URIRef(value)  # Wrap URLs as URIRef
            else:
                obj = Literal(value)  # Keep non-URL values as literals
            g.add((pid_uri, predicate, obj))

    g.serialize(destination=output_RDF_file, format="turtle")
    print(f"RDF data has been written to '{output_RDF_file}'.")


def is_valid_url(value):
    """
    Check if a given value is a valid URL.

    This function determines whether a string follows a proper URL format.
    It uses Python's `urllib.parse.urlparse` to check if the value contains:
    - A valid scheme (e.g., 'http', 'https')
    - A valid network location (netloc), such as a domain name.

    This is useful for distinguishing between URLs (which should be stored as
    `URIRef` in RDF) and regular string literals.

    Args:
        value (str): The value to check.

    Returns:
        bool: True if the value is a valid URL, False otherwise.

    Example:
        >>> is_valid_url("https://example.org/resource")
        True
        >>> is_valid_url("not_a_url")
        False
    """
    try:
        parsedURL = urlparse(value)
        # print (result)
        return all(
            [parsedURL.scheme, parsedURL.netloc]
        )  # Must have a scheme (http, https) and a domain
    except:
        return False


def load_sssom_data(mapping_source):
    """
    Load SSSOM data from either a local file or a URL.

    Args:
        mapping_source (str): Path to a local file or URL.

    Returns:
        str: The raw content of the SSSOM mapping file.
    """
    if os.path.isfile(mapping_source):  # Check if it's a local file
        try:
            with open(mapping_source, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading local SSSOM file '{mapping_source}': {e}")
            sys.exit(1)
    else:  # Assume it's a URL
        try:
            response = requests.get(mapping_source)
            response.raise_for_status()  # Check if request was successful
            return response.text  # Get file content as string
        except requests.exceptions.RequestException as e:
            print(f"Error fetching SSSOM file from URL '{mapping_source}': {e}")
            sys.exit(1)


def main():
    """
    Command-line tool for converting JSON data into RDF using SSSOM mappings.

    This tool reads JSON data containing records, applies mappings from an SSSOM file,
    and converts the data into RDF format, saving it in a Turtle (.ttl) file.

    Features:
    - Supports CURIE prefixes extracted from the SSSOM file.
    - Allows input from a local file or a URL.
    - Generates RDF triples with subject-predicate-object structure.
    - Saves the output in Turtle format.

    Arguments:
        --json          Path to the input JSON file.
        --mappingsFile  Path or URL to the SSSOM mapping file.
        --output        Path to the output RDF file.
        --version       Show version information and exit.
        -h, --help      Show help message and usage instructions.

    Example Usage:
        python FDO2RDF.py --json data.json --mappingsFile mappings.sssom.tsv --output output.ttl
    """

    parser = argparse.ArgumentParser(
        description="Convert JSON data to RDF in Turtle format using SSSOM mappings."
    )

    parser.add_argument("--json", required=True, help="Path to the input JSON file.")

    parser.add_argument(
        "--mappingsFile", required=True, help="Path or URL to the SSSOM mapping file."
    )

    parser.add_argument(
        "--output",
        required=False,
        default="FDO-triples.ttl",
        help="Path to the output RDF Turtle file (default: FDO-triples.ttl).",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="1.0.0",
        help="Show program version and exit.",
    )

    args = parser.parse_args()

    json_file = args.json
    mapping_source = args.mappingsFile
    output_RDF_file = args.output

    # Fetch SSSOM data (from URL or local file)
    if mapping_source.startswith("http"):
        try:
            response = requests.get(mapping_source)
            response.raise_for_status()
            sssom_data = response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching SSSOM file from URL: {e}")
            sys.exit(1)
    else:
        try:
            with open(mapping_source, encoding="utf-8") as file:
                sssom_data = file.read()
        except FileNotFoundError:
            print(f"Error: SSSOM file '{mapping_source}' not found.")
            sys.exit(1)

    # Load JSON data
    try:
        with open(json_file, encoding="utf-8") as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file '{json_file}' not found.")
        sys.exit(1)

    if isinstance(json_data, dict):
        json_data = [json_data]  # Wrap in list if it's a single object

    # Extract CURIE prefixes and parse SSSOM mappings
    curie_map = extract_prefixes_from_sssom(sssom_data)
    sssom_mappings = parse_sssom_mapping(sssom_data, curie_map)

    # Convert JSON data to RDF
    convert_json_to_rdf(json_data, curie_map, sssom_mappings, output_RDF_file)


if __name__ == "__main__":
    main()
