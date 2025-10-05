# Step1: Access arXiv using URL
import requests

def search_arxiv_papers(query: str, max_results: int = 5) -> dict:
    """Search for papers on arXiv based on a query string."""

    query = "+".join(query.lower().split())
    for char in ['(', ')', ':', ';', ',']:
        if char in query:
            query = query.replace(char, "")
    
    url = {
        "url": f"https://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"
    }

    print(f"Searching arXiv with URL: {url['url']}")
    response = requests.get(url["url"])

    if not response.ok:
        print(f"ArXiv API request failed with status code {response.status_code} - {response.text}")
        raise ValueError("ArXiv API request failed")
    data = parse_arxiv_xml_response(response.text)
    return data

# Step2: Parse XML response
def parse_arxiv_xml_response(xml_response: str) -> dict:
    """Parse the XML response from arXiv API and extract paper details."""
    import xml.etree.ElementTree as ET

    root = ET.fromstring(xml_response)
    namespace = {
        'atom': 'http://www.w3.org/2005/Atom', 
        'arxiv': 'http://arxiv.org/schemas/atom'
        }
    papers = []

    for entry in root.findall('atom:entry', namespace):
        # Extract PDF link safely
        pdf_link = None
        for link in entry.findall('atom:link', namespace):
            if link.attrib.get('type') == 'application/pdf':
                pdf_link = link.attrib['href']
                break
        paper = {
            'title': entry.find('atom:title', namespace).text.strip() if entry.find('atom:title', namespace) is not None and entry.find('atom:title', namespace).text is not None else "", # pyright: ignore[reportOptionalMemberAccess]
            'summary': entry.find('atom:summary', namespace).text.strip() if entry.find('atom:summary', namespace) is not None and entry.find('atom:summary', namespace).text is not None else "", # pyright: ignore[reportOptionalMemberAccess]
            'authors': [author.find('atom:name', namespace).text for author in entry.findall('atom:author', namespace)], # type: ignore
            'pdf_link': pdf_link,
            'categories': [category.attrib['term'] for category in entry.findall('atom:category', namespace)]
        }
        papers.append(paper)

    return {'papers': papers}

print(search_arxiv_papers("machine learning", max_results=2))

#step3: Convert to functionality into a tool for agentic-ai-researcher
from langchain_core.tools import tool

@tool
def arxiv_search_tool(query: str, max_results: int = 5) -> list[dict]:
    """Search for recently published arxiv papers
    Args:
        query (str): The search query string.
        max_results (int, optional): Maximum number of results to return. Defaults to 5.
    Returns:
        list[dict]: A list of dictionaries containing paper details.
    """
    print("ARXIV Agent called")
    print(f"Searching arXiv for papers about: {query}")
    papers = search_arxiv_papers(query, max_results)
    if len(papers['papers']) == 0:
        return [{"title": "No papers found", "summary": "", "authors": [], "pdf_link": "", "categories": []}]   
    else:
        return papers['papers']
    
