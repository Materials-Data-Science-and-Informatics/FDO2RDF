
# FDO2RDF Tool

This tool converts FAIR digital objects metadata in JSON into RDF triples using Simple Standardized Ontology Mappings (SSSOM) for mapping subject identifiers to object identifiers (RDF predicates). FDO2RDF processes the input JSON data, applies SSSOM mappings (either provided as a file on the local file system or a URL), and outputs the data in Turtle (`.ttl`) format.


## Features

- **Convert JSON to RDF**: The main function of FDO2RDF is to convert FDO metadata in JSON into RDF triples using mappings from an SSSOM file.
- **Flexible Input and Output**: allows you to specify input files for both the JSON data and the SSSOM mapping, as well as the output RDF file.
- **Turtle Format**: outputs RDF triples in Turtle (`.ttl`) format.
- **SSOM mappings**: process provided mappings file in TSV either as a file on the local file system or a URL.

## Requirements

- **Python 3.x**: The tool is compatible with Python 3.
- **Required Libraries**:
  - `pandas`: for reading and processing the SSSOM file.
  - `rdflib`: for creating and manipulating RDF graphs.
  - `argparse`: for handling command-line arguments.
  - `requests`: for handeling HTTP requests.


## **Installation**

You can install `fdo2rdf` directly from the source:

```bash
git clone https://github.com/Materials-Data-Science-and-Informatics/FDO2RDF.git
cd FDO2RDF
pip install .

```



## Usage

To run the tool, you can use the following command:

```bash
fdo2rdf --json 'src/fdo2rdf/samples/sample-FDO.json' --mappingsFile 'src/fdo2rdf/mappings/Helmholtz-KIP-mappings.tsv'
```
You can either specify the output file using the `--output` parameter, or it will be automatically generated into the local directory as `FDO-triples.ttl`.

### Arguments

- **--json**
  - **Description**: Specify the path to the input JSON file.
  - **Required**: Yes

- **--mappingsFile**

  - **Description**: Provide the URL or path to the SSSOM mapping file (in **TSV format**).
  - **Required**: Yes

- **--output**

  - **Description**: Specify the path to the output **RDF Turtle** file.
  - **Required**: No

- **--version**

  - **Description**: Print the version of the tool.
  - **Required**: No.

- **--help**

  - **Description**: Show the help message with all available arguments.
  - **Required**: No.

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


## Acknowledgments <a name="Acknowledgements"></a>

<div>
<img style="vertical-align: middle;" alt="HMC Logo" src="https://github.com/Materials-Data-Science-and-Informatics/Logos/raw/main/HMC/HMC_Logo_M.png" width=50% height=50% />
&nbsp;&nbsp;
<img style="vertical-align: middle;" alt="FZJ Logo" src="https://github.com/Materials-Data-Science-and-Informatics/Logos/raw/main/FZJ/FZJ.png" width=30% height=30% />
</div>
<br />

This project was developed at the Institute for Materials Data Science and Informatics
(IAS-9) of the Jülich Research Center and funded by the Helmholtz Metadata Collaboration
(HMC), an incubator-platform of the Helmholtz Association within the framework of the
Information and Data Science strategic initiative.

---


For any questions or issues, please open an issue on the GitHub repository.
