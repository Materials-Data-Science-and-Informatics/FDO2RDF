import argparse
from io import StringIO
import json
import os
import sys
import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
import csv

# CURIE Prefix Map from the SSSOM file
CURIE_MAP = {
    "hdo": "https://purls.helmholtz-metadaten.de/hob/HDO",
    "schema": "https://schema.org/",
    "orcid": "https://orcid.org/",
    "hdl": "https://hdl.handle.net/",
    "provo": "http://www.w3.org/ns/prov#",
    "semapv": "https://w3id.org/semapv/vocab/",
    "dcterms": "http://purl.org/dc/terms/",
    "dcversion": "http://dublincore.org/usage/terms/history/",
    "skos": "http://www.w3.org/2004/02/skos/core#"
}

def curie_to_uri(curie):
    """
    Converts CURIE (Compact URI) to a full URI using the provided CURIE prefix map.
    """
    prefix, suffix = curie.split(":", 1)
    if prefix in CURIE_MAP:
        return CURIE_MAP[prefix] + suffix
    else:
        return curie  # Return as-is if prefix is not found
def get_namespace_for_prefix(prefix):
    # Example prefix-to-namespace mappings (this can be extended)
        prefix_map = {
        "hdl": "https://hdl.handle.net/",
        "schema": "https://schema.org/",
        "hdo": "https://purls.helmholtz-metadaten.de/hob/",
        "provo": "http://www.w3.org/ns/prov#",
        "other": "http://other.namespace.org/"
        # Add more prefix mappings as needed
        }
        return prefix_map.get(prefix)  # Default namespace for unknown prefixes

def parse_sssom_mapping(sssom_file):
    """
    Parse the SSSOM file and return a mapping of subject_id to object_id (which will be used as predicates).
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
                namespace = get_namespace_for_prefix(prefix)
                json_key = URIRef(f"{namespace}{subject_id}")
            else:
                json_key = URIRef(json_key).strip()  # If no prefix, use it as a direct URI
            
            # print("subject="+json_key)

            # Handle CURIE for ontology_property (predicate)
            if ':' in ontology_property:
                prefix, object_id = ontology_property.split(":", 1)
                namespace = get_namespace_for_prefix(prefix)
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
    
def extract_prefixes_from_sssom(sssom_file_path):
    curie_map = {}

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

def convert_json_to_rdf(json_data, sssom_data,sssom_file_path,output_RDF_file):
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
    output_file = args.output if args.output else "debug_output.ttl"

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

    # Load SSSOM mapping
    sssom_mappings = parse_sssom_mapping(mapping_file)

    # Convert the JSON to RDF in Turtle format
    output_RDF_file="FDO-sample.ttl"
    convert_json_to_rdf(json_data, sssom_mappings,mapping_file, output_RDF_file)

if __name__ == "__main__":
    main()

#python FDO2RDF.py --json sample_fdo.json --mapping FDO_map.sssom.tsv --output my_output.ttl