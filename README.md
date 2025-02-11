
# FDO2RDF Tool

This tool converts JSON data into RDF format using Simple Standardized Ontology Mappings (SSSOM) for mapping subject identifiers to object identifiers (RDF predicates). The tool processes the input JSON data, applies SSSOM mappings, and outputs the data in Turtle (`.ttl`) format.

 
## Features

- **Convert JSON to RDF**: The main function of FDO2RDF is to convert FDO metadata in JSON into RDF triples using mappings from an SSSOM file.
- **Flexible Input and Output**: This tool allows you to specify input files for both the JSON data and the SSSOM mapping, as well as the output RDF file.
- **Turtle Format**: The output is saved in Turtle (`.ttl`) format, a widely used RDF serialization format.

## Requirements

- **Python 3.x**: The tool is compatible with Python 3.
- **Required Libraries**:
  - `pandas`: For reading and processing the SSSOM file.
  - `rdflib`: For creating and manipulating RDF graphs.
  - `argparse`: For handling command-line arguments.

You can install the required dependencies by running the following command:

```bash
pip install pandas rdflib
```
 

## **Installation**

1. Clone the repository:

```bash
git clone https://github.com/yourusername/json-to-rdf-converter.git
cd json-to-rdf-converter
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

 

## Usage

To run the tool, you can use the following command:

```bash
python FDO2RDF.py --json <input_json_file> --mappingsFile <sssom_file> --output <output_rdf_file>
```

### Arguments

- **--json**
  - **Description**: Specify the path to the input JSON file.
  - **Required**: No 
  
- **--mappingsFile**

  - **Description**: Provide the URL or path to the SSSOM mapping file (in **TSV format**).
  - **Required**: No 
  
- **--output**

  - **Description**: Specify the path to the output **RDF Turtle** file.
  - **Required**: No 
  
- **--version**

  - **Description**: Print the version of the tool.
  - **Required**: No.
  
- **--help**

  - **Description**: Show the help message with all available arguments.
  - **Required**: No.

### Example Command

```bash
python FDO2RDF.py --json sample_fdo.json --mappingsFile FDO_map.sssom.tsv --output my_output.ttl
```

## File Format

### Input JSON

The input is a JSON file which is structured as a list of objects representing [FDO metadata](https://kit-data-manager.github.io/fairdoscope/?pid=21.11152/6ea60288-d895-414e-80c0-26c9fdd662b2):

- `pid`: The Persistent Identifier (PID) for the record, which will be converted to a URI.
- `record`: A list of key-value pairs, where:
  - `key`: A CURIE subject identifier (e.g., `schema:name`).
  - `value`: A literal value associated with the subject.

Example:

```json
{
    "pid": "https://hdl.handle.net/21.11152/6ea60288-d895-414e-80c0-26c9fdd662b2",
    "record": [
        {
            "key": "https://hdl.handle.net/21.T11148/397d831aa3a9d18eb52c",
            "value": "2022-08-19T00:00:00+00:00"
        },
        {
            "key": "https://hdl.handle.net/21.T11148/82e2503c49209e987740",
            "value": "{ \"md5sum\": \"f133dd7d1faacf15a434e2e8ece0d57b\" }"
        },
        {
            "key": "https://hdl.handle.net/21.T11148/c692273deb2772da307f",
            "value": "1.0.0"
        },
        {
            "key": "https://hdl.handle.net/21.T11148/aafd5fb4c7222e2d950a",
            "value": "2022-08-19T00:00:00+00:00"
        }
    ]
}

```

### SSSOM Mapping File

The SSSOM mapping file should be in TSV (tab-separated values) format, with two key columns:

- `subject_id`: The CURIE subject identifier (e.g., `schema:name`).
- `object_id`: The corresponding RDF predicate URI.

Example:

```tsv
#curie_map:
#   hdo: https://purls.helmholtz-metadaten.de/hob/HDO_
#   schema: https://schema.org/
#   hdl: https://hdl.handle.net/
#   provo: http://www.w3.org/ns/prov#
subject_id	subject_label	predicate_id	object_id	object_label	mapping_justification	author_id	mapping_date
hdl:21.T11148/c085f1292d7d4a338d96	wasGeneratedBy	skos:broadMatch	provo:wasGeneratedBy	wasGeneratedBy	semapv:ManualMappingCuration	https://orcid.org/0000-0002-4366-3088	2023-03-03
hdl:21.T11148/076759916209e5d62bd5	kernelInformationProfile	skos:exactMatch	hdo:00006065	follows kernel information profile	semapv:ManualMappingCuration	https://orcid.org/0000-0002-2818-5890	2025-01-31
hdl:21.T11148/1c699a5d1b4ad3ba4956	digitalObjectType	skos:exactMatch	hdo:00006080	has digital object type	semapv:ManualMappingCuration	https://orcid.org/0000-0002-2818-5890	2025-01-31
hdl:21.T11148/29f92bd203dd3eaa5a1f	dateCreated	skos:exactMatch	schema:dateCreated	dateCreated	semapv:ManualMappingCuration	https://orcid.org/0000-0002-2818-5890	2025-01-31

```

## How It Works

1. **Extract CURIE Prefixes**: The tool extracts CURIE prefixes and their corresponding full URIs from the provided SSSOM file.
2. **Parse SSSOM Mapping**: The tool maps the `subject_id` from the input JSON to the corresponding `object_id` (predicate) based on the SSSOM mappings.
3. **Convert JSON to RDF**: The tool creates an RDF graph where each JSON object is translated into RDF triples, using the extracted CURIE prefixes for URIs and literals for values.
4. **Output Turtle File**: The resulting RDF graph is serialized into Turtle format and saved to the specified output file.

## Example Output (Turtle Format)

The output RDF will be saved in Turtle format, which will look like this:

```ttl
@prefix hdo: <https://purls.helmholtz-metadaten.de/hob/> .
@prefix schema: <https://schema.org/> .

<https://hdl.handle.net/21.11152/6ea60288-d895-414e-80c0-26c9fdd662b2> hdo:HDO_00006065 "21.T11148/b9b76f887845e32d29f7" ;
    hdo:HDO_00006068 "http://vocabularies.unesco.org/thesaurus/concept1557",
        "http://vocabularies.unesco.org/thesaurus/concept3052" ;
    hdo:HDO_00006070 "21.11152/041a6111-644a-4617-afb3-3c421a88e8e3",
        "21.11152/365fd8cf-8e86-41b8-9d0e-b816fdd01d29",
        "21.11152/3ab9f444-05f6-445e-a691-62fae4021bea",
        "21.11152/6858a0b5-cc60-40e9-afef-8c2dd8b35e8e",
        "21.11152/e670f510-7e00-4d3a-9b90-3bac7a7c069e" ;
    hdo:HDO_00006077 "{ \"md5sum\": \"f133dd7d1faacf15a434e2e8ece0d57b\" }" ;
    hdo:HDO_00006080 "21.11152/ba06424b-17c7-4e3f-9a2e-8d09cf797be3" ;
    schema:contactPoints "https://orcid.org/0000-0001-9930-5354",
        "https://orcid.org/0000-0002-2233-1041",
        "https://orcid.org/0000-0002-8059-4149",
        "https://orcid.org/0000-0002-8517-2359",
        "https://orcid.org/0000-0002-9082-9095",
        "https://orcid.org/0000-0002-9822-244X" ;
    schema:contentUrl "https://zenodo.org/record/6517768/files/Flug1_100-104Media_coco.json?download=1" ;
    schema:dateCreated "2022-08-19T00:00:00+00:00" ;
    schema:dateModified "2022-08-19T00:00:00+00:00" ;
    schema:license "https://creativecommons.org/licenses/by/4.0/" ;
    schema:version "1.0.0" .
```

## Contributing

Contributions are welcome! If you would like to contribute to this project, feel free to fork the repository and submit a pull request with your improvements or bug fixes.

## License

This tool is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

For any questions or issues, please open an issue on the GitHub repository.
