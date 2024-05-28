
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain.chains import create_extraction_chain
import pprint
from langchain_openai import ChatOpenAI

def extract(content: str, schema: dict,llm):
    return create_extraction_chain(schema=schema, llm=llm).run(content)

def scrape_with_playwright(urls, schema,llm):
    loader = AsyncChromiumLoader(urls)
    docs = loader.load()
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(
        docs, tags_to_extract=["span"]
    )
    print("Extracting content with LLM")

    # Grab the first 1000 tokens of the site
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=0
    )
    splits = splitter.split_documents(docs_transformed)

    # Process the first split
    for split in splits:
        extracted_content = extract(schema=schema, content=split.page_content,llm = llm)
        pprint.pprint(extracted_content)
    pprint.pprint(extracted_content)
    return extracted_content
