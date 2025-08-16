import pytest
from unittest.mock import patch, MagicMock
import requests
from tools import search_pubmed, analyze_sequence, calculate_drug_properties

# --- Tests for search_pubmed ---

@patch('tools.requests.get')
def test_search_pubmed_success(mock_get):
    """
    Tests successful PubMed search by mocking the requests library.
    """
    # Mock the response from the initial search (for PMIDs)
    mock_search_response = MagicMock()
    mock_search_response.status_code = 200
    mock_search_response.json.return_value = {
        "esearchresult": {"idlist": ["12345", "67890"]}
    }
    
    # Mock the response from the fetch call (for article details)
    mock_fetch_response = MagicMock()
    mock_fetch_response.status_code = 200
    # A simplified XML response for testing
    mock_fetch_response.content = b'''
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation Status="MEDLINE" Owner="NLM">
                <PMID Version="1">12345</PMID>
                <Article>
                    <ArticleTitle>Test Title 1</ArticleTitle>
                    <Abstract>
                        <AbstractText>This is a test abstract.</AbstractText>
                    </Abstract>
                </Article>
            </MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>
    '''
    
    # The first call to requests.get is for search, the second is for fetch
    mock_get.side_effect = [mock_search_response, mock_fetch_response]

    result = search_pubmed("crispr")
    
    assert result["num_results"] == 1
    assert result["results"][0]["title"] == "Test Title 1"
    assert "This is a test abstract" in result["results"][0]["abstract"]
    assert result["results"][0]["pmid"] == "12345"

@patch('tools.requests.get')
def test_search_pubmed_no_results(mock_get):
    """
    Tests PubMed search with no results found.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"esearchresult": {"idlist": []}}
    mock_get.return_value = mock_response

    result = search_pubmed("some obscure query")
    assert result["num_results"] == 0
    assert len(result["results"]) == 0

@patch('tools.requests.get')
def test_search_pubmed_api_error(mock_get):
    """
    Tests handling of an API error during PubMed search.
    """
    mock_get.side_effect = requests.exceptions.RequestException("API is down")

    result = search_pubmed("any query")
    assert "error" in result
    assert "API request failed" in result["error"]


# --- Tests for analyze_sequence ---

def test_analyze_dna_sequence():
    """
    Tests analysis of a valid DNA sequence.
    """
    dna = "ATGCGC"
    result = analyze_sequence(dna, "DNA")
    assert result["length"] == 6
    assert result["gc_content"] == "66.67%"
    assert result["transcription"] == "AUGCGC"
    assert result["translation"] == "MR"

def test_analyze_rna_sequence():
    """
    Tests analysis of a valid RNA sequence.
    """
    rna = "AUGCGC"
    result = analyze_sequence(rna, "RNA")
    assert result["length"] == 6
    assert result["back_transcription"] == "ATGCGC"

def test_analyze_invalid_sequence_type():
    """
    Tests that an invalid sequence type returns an error.
    """
    result = analyze_sequence("ATGC", "invalid_type")
    assert "error" in result


# --- Tests for calculate_drug_properties ---

def test_calculate_aspirin_properties():
    """
    Tests property calculation for a valid SMILES string (Aspirin).
    """
    aspirin_smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"
    result = calculate_drug_properties(aspirin_smiles)
    assert "error" not in result
    assert round(result["molecular_weight"], 2) == 180.16
    assert round(result["logp"], 2) == 1.31
    assert result["hbd"] == 1
    assert result["hba"] == 3

def test_calculate_invalid_smiles():
    """
    Tests that an invalid SMILES string returns an error.
    """
    result = calculate_drug_properties("this is not a smiles string")
    assert "error" in result
    assert result["error"] == "Invalid SMILES string provided."
