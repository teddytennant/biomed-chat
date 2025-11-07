"""
Biomedical engineering tools for the chatbot.
These are functional implementations using public APIs and libraries.
"""
import requests

# Optional dependencies for biomedical tools
try:
    from Bio.Seq import Seq
    from Bio.SeqUtils import gc_fraction
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Lipinski
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False

def search_pubmed(query: str, max_results: int = 3) -> dict:
    """
    Search PubMed for biomedical literature using the NCBI E-utilities API.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    search_url = f"{base_url}esearch.fcgi"
    fetch_url = f"{base_url}efetch.fcgi"

    try:
        # Step 1: Search for PMIDs
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
        }
        search_response = requests.get(search_url, params=search_params, timeout=10)
        search_response.raise_for_status()
        search_data = search_response.json()
        pmids = search_data.get("esearchresult", {}).get("idlist", [])

        if not pmids:
            return {"query": query, "num_results": 0, "results": []}

        # Step 2: Fetch details for the PMIDs
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
        }
        fetch_response = requests.get(fetch_url, params=fetch_params, timeout=10)
        fetch_response.raise_for_status()
        
        # Using ElementTree to parse the XML response
        from xml.etree import ElementTree
        root = ElementTree.fromstring(fetch_response.content)
        results = []
        for article in root.findall(".//PubmedArticle"):
            title_element = article.find(".//ArticleTitle")
            title = title_element.text if title_element is not None else "No title found"
            
            abstract_element = article.find(".//Abstract/AbstractText")
            abstract = abstract_element.text if abstract_element is not None else "No abstract available."

            pmid_element = article.find(".//PMID")
            pmid = pmid_element.text if pmid_element is not None else ""

            results.append({
                "title": title,
                "abstract": abstract[:500] + '...' if abstract and len(abstract) > 500 else abstract,
                "pmid": pmid,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
            })

        return {"query": query, "num_results": len(results), "results": results}

    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

def analyze_sequence(sequence: str, sequence_type: str) -> dict:
    """
    Analyze DNA, RNA, or protein sequences using Biopython.
    """
    if not BIOPYTHON_AVAILABLE:
        return {
            "error": "Biopython is not installed. Install it with: pip install biopython"
        }
    
    try:
        seq_upper = sequence.upper().strip()
        bio_seq = Seq(seq_upper)
        analysis = {
            "sequence_type": sequence_type,
            "length": len(bio_seq),
        }

        if sequence_type == "DNA":
            analysis["gc_content"] = f"{gc_fraction(bio_seq) * 100:.2f}%"
            analysis["transcription"] = str(bio_seq.transcribe())
            analysis["translation"] = str(bio_seq.translate())
        elif sequence_type == "RNA":
            analysis["gc_content"] = f"{gc_fraction(bio_seq) * 100:.2f}%"
            analysis["back_transcription"] = str(bio_seq.back_transcribe())
            analysis["translation"] = str(bio_seq.translate())
        elif sequence_type == "protein":
            # Placeholder for protein-specific analysis
            analysis["molecular_weight"] = "Not yet implemented."
        else:
            return {"error": "Invalid sequence_type. Must be 'DNA', 'RNA', or 'protein'."}

        return analysis
    except Exception as e:
        return {"error": f"An error occurred during sequence analysis: {str(e)}"}

def calculate_drug_properties(smiles: str) -> dict:
    """
    Calculate molecular properties for a drug compound from its SMILES string using RDKit.
    """
    if not RDKIT_AVAILABLE:
        return {
            "error": "RDKit is not installed. Install it with: pip install rdkit"
        }
    
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {"error": "Invalid SMILES string provided."}

        properties = {
            "molecular_weight": Descriptors.MolWt(mol),
            "logp": Descriptors.MolLogP(mol),
            "hbd": Lipinski.NumHDonors(mol),
            "hba": Lipinski.NumHAcceptors(mol),
            "rotatable_bonds": Lipinski.NumRotatableBonds(mol),
            "tpsa": Descriptors.TPSA(mol),
        }
        return properties
    except Exception as e:
        return {"error": f"An error occurred during property calculation: {str(e)}"}

# Placeholder for other tools from the config, returning a simple message.
def simulate_pharmacokinetics(**kwargs) -> dict:
    return {"status": "This tool is not yet implemented."}

def analyze_medical_image(**kwargs) -> dict:
    return {"status": "This tool is not yet implemented."}
