import argparse
from io import StringIO
import json
import os
import sys
import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
import csv


def extract_prefixes_from_sssom(sssom_file_path):
    """
    Extracts CURIE prefixes from an SSSOM file.

    Args:
        sssom_file_path (str): Path to the SSSOM file.

    Returns:
        dict: A dictionary mapping CURIE prefixes to their full URIs.
    """
    curie_map = {}

    if not sssom_file_path or not os.path.exists(sssom_file_path):
        print(f"Error: Invalid or missing SSSOM file path '{sssom_file_path}'")
        sys.exit(1)
    with open(sssom_file_path, 'r') as file:
        lines = file.readlines()

        # Flag to indicate if we're inside the #curie_map section
        in_curie_map_section = False

        for line in lines:
            # Skip empty lines and comments
            if line.startswith("#curie_map"):
                in_curie_map_section = True  # We are inside the curie_map section now
                continue
            if line.strip().startswith("#mapping_set_id"):
                in_curie_map_section =False

            if in_curie_map_section and ":" in line:
                # Extract prefix and URI from lines in the curie_map section
                parts = line.split(":", 1)  # Only split on the first colon
                # print(parts[0])
                if len(parts) == 2 and line != "#curie_map":
                    prefix = parts[0].strip().lstrip("#").lstrip()
                    uri = parts[1].strip()
                    curie_map[prefix] = uri
                    #print(prefix[3:]+"::::"+uri)
                
    # Return the extracted CURIE Prefix Map as a dictionary
    return curie_map
def get_namespace_for_prefix(prefix, curie_map):
    """
    Retrieve the full namespace (URI) for a given CURIE prefix from the provided CURIE map.

    Args:
        prefix (str): The CURIE prefix (e.g., 'schema', 'dcterms', etc.) that needs to be resolved into a full URI. 
        curie_map (dict): A dictionary mapping CURIE prefixes to their full URIs (e.g., {'schema': 'https://schema.org/'}) 

    Returns:
        str: The corresponding full URI for the given prefix, or an empty string if the prefix is not found.
    """
    return curie_map.get(prefix, "")

def parse_sssom_mapping(sssom_file, curie_map):
    """
    Parses an SSSOM mapping file and returns a dictionary mapping subject_id to object_id.
    
    Args:
        sssom_file (str): Path to the SSSOM TSV file.
        curie_map (dict): Dictionary of CURIE prefixes extracted from the SSSOM file.

    Returns:
        dict: Mapping of subject_id to object_id (RDF predicates).
    """
    print(f"Parsing SSSOM mappings from '{sssom_file }' ...")

    try:
        mapping = {}
        sssom_data = pd.read_csv(sssom_file, sep="\t", comment="#")
        
        for _, row in sssom_data.iterrows():
            json_key = row["subject_id"]  # JSON key (from record)
            ontology_property = row["object_id"]  # Ontology property (RDF predicate)
            

            # Process CURIE (e.g., ex:subjectID -> http://example.org/subjectID)
            if ':' in json_key:
                prefix, subject_id = json_key.split(":", 1)
                namespace = get_namespace_for_prefix(prefix, curie_map)
                json_key = URIRef(f"{namespace}{subject_id}")
            else:
                json_key = URIRef(json_key).strip()  # If no prefix, use it as a direct URI
            
            # print("subject="+json_key)

            # Handle CURIE for ontology_property (predicate)
            if ':' in ontology_property:
                prefix, object_id = ontology_property.split(":", 1)
                namespace = get_namespace_for_prefix(prefix, curie_map)
                ontology_property = URIRef(f"{namespace}{object_id}")
            else:
                ontology_property = URIRef(ontology_property)

            # print("key= "+ json_key+ " object=  "+ontology_property)
            
            mapping[json_key] = ontology_property
            # print(json_key+"-to->"+ontology_property)
            #print(mapping["21.T11148/397d831aa3a9d18eb52c"])
        """ for line in mapping:
            print(mapping)   """
    except Exception as e:
        print(f"Error reading SSSOM mapping file: {e}")
        sys.exit(1)
    return mapping
    


def convert_json_to_rdf(json_data, sssom_data,sssom_file_path,output_RDF_file):
    """
    Converts the input JSON data into RDF format using the SSSOM mappings, and writes the output to a Turtle file.

    Args:
        json_data (list): A list of JSON objects containing the data to be converted into RDF. Each object in the list represents a record with specific fields, such as `pid`, `record`, `key`, and `value`.
        sssom_data (dict): A dictionary mapping the subject identifiers (keys) to their corresponding RDF predicates (object identifiers) based on the SSSOM mappings.
        sssom_file_path (str): The path to the SSSOM file used for extracting CURIE mappings, which will be utilized for resolving subject and object identifiers.
        output_RDF_file (str): The path where the generated RDF data in Turtle format will be saved.

    Returns:
        None: The function does not return any value but saves the resulting RDF data to a file.
    """
    mapping = {}
    reader = csv.DictReader(str(sssom_data).strip(), delimiter="\t")

    #for row in sssom_data:
        #print("Parsed Row:", row +"    and    "+sssom_data[row])  # Debugging: Show parsed row
        # mapping[row["subject_id"].strip()] = row["object_id"].strip()
    curie_map = extract_prefixes_from_sssom(sssom_file_path)
# Create an RDF graph
    g = Graph()

    for prefix, uri in curie_map.items():
        g.bind(prefix, Namespace(uri))
        # print("prefixes: "+prefix+"---"+Namespace(uri))
    """ SCHEMA = Namespace("https://schema.org/")
    HDO = Namespace("https://purls.helmholtz-metadaten.de/hob/")
    g.bind("schema", SCHEMA)
    g.bind("hdo", HDO)
 """ 
    # print added prefixes to the graph
    """ for prefix, namespace in g.namespaces():
        print(f"{prefix}: {namespace}")  """
# Process JSON data and add RDF triples
    # print(json_data['pid'])
    # pid = URIRef(f"https://hdl.handle.net/{json_data['pid']}")
    # Process each object in the list
    # Process each object in the list
    for obj in json_data:
        pid = obj["pid"]  # Access the PID
        pid_uri = URIRef(pid)  # Convert PID to URIRef

    # Iterate through the records
        for record in obj["record"]:
            key = record["key"]  # Extract the key
            value = record["value"]  # Extract the value

              

    # Map the key to the corresponding predicate using SSSOM
            try:
                predicate_uri = sssom_data[URIRef(key)]
            except KeyError:
                print(f"** Warning: {key} has no mapping!")
            if not predicate_uri:
                print(f"Skipping invalid record: {key}")
                continue

    # Add triple: subject (pid), predicate (mapped URI), object (value)
            predicate = URIRef(predicate_uri)
            obj = Literal(value)
            g.add((pid_uri, predicate, obj))

# Serialize and output the RDF
    g.serialize(destination=output_RDF_file, format='turtle')
    print(f"RDF data has been written to '{output_RDF_file}' file.")

def main():
   
    parser = argparse.ArgumentParser(description="Convert JSON data to RDF in Turtle format using SSSOM mappings.")
    parser.add_argument("--json", required=False, help="Path to the input JSON file")
    parser.add_argument("--mappingsFile", required=False, help="Path to the SSSOM mapping file (TSV format)")
    parser.add_argument("--output", required=False, help="Path to the output Turtle file (default: debug_output.ttl)")
    args = parser.parse_args()

    # Default filenames for debugging
    # json_file = args.json if args.json else "sample_fdo.json"
    json_file = args.json if args.json else "sample_fdo+children.json"
    mapping_file = args.mappingsFile if args.mappingsFile else "FDO_map.sssom.tsv"
    output_RDF_file = args.output if args.output else "FDO-sample.ttl"

    # Load JSON data
    try:
        with open(json_file, "r") as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file '{json_file}' not found.")
        sys.exit(1)
    
    # Ensure that json_data is a list, even if it's a single object
    if isinstance(json_data, dict):
        json_data = [json_data]  # Wrap the single object in a list

    # Ensure that parameter files exist or parameters are given
    """ try:
        os.path.exists(args.json)
    except TypeError:
        print(f"Error: JSON file '{json_file}' not found or --json parameter is not given.")
        sys.exit(1)

    try:
        os.path.exists(args.mapping)   
    except TypeError:
        print(f"Error: SSSOM file '{mapping_file}' not found or --mapping parameter is not given.")
        sys.exit(1) """

    curie_map = extract_prefixes_from_sssom(mapping_file)
    # Load SSSOM mapping
    sssom_mappings = parse_sssom_mapping(mapping_file, curie_map)

    # Convert the JSON to RDF in Turtle format
    # output_RDF_file="FDO-sample.ttl"
    convert_json_to_rdf(json_data, sssom_mappings,mapping_file, output_RDF_file)

if __name__ == "__main__":
    main()

#python FDO2RDF.py --json sample_fdo.json --mapping FDO_map.sssom.tsv --output my_output.ttl
