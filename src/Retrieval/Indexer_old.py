# os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import faiss, re
import torch
import numpy as np

from transformers import AutoTokenizer, AutoModel
from sklearn.feature_extraction.text import TfidfVectorizer
from Preprocessing import PreProcessorOld


def paragraph_chunks_v2(text: str, chunk_size: int = 300) -> list:
    lines = text.split('\n\n')

    chunks = []
    current_chunk = ""
    paragraph_context = []

    for line in lines:
        if line.startswith('§'):
            if current_chunk:
                chunks.append((current_chunk.strip(), paragraph_context))
            current_chunk = line
            paragraph_context = [line]
        else:
            current_chunk += " " + line
            paragraph_context.append(line)

    if current_chunk:
        chunks.append((current_chunk.strip(), paragraph_context))

    # Split chunks into equal size chunks
    equal_size_chunks = []
    for chunk, context in chunks:
        for i in range(0, len(chunk), chunk_size):
            equal_size_chunks.append((chunk[i:i + chunk_size], context))

    return equal_size_chunks

def paragraph_chunks_v3(text: str) -> list:
    lines = text.split('\n\n')

    chunks = []
    current_chunk = ""
    paragraph_context = []

    for line in lines:
        if line.startswith('§'):
            if current_chunk:
                chunks.append((current_chunk.strip(), paragraph_context))
            current_chunk = line
            paragraph_context = [line]
        else:
            current_chunk += " " + line
            paragraph_context.append(line)

    if current_chunk:
        chunks.append((current_chunk.strip(), paragraph_context))

    # Split chunks into single sentences
    sentence_chunks = []
    for chunk, context in chunks:
        # sentences = re.split(r'(?<=[.!?]) +', chunk)
        sentences = re.split(r'(?<!Abs)(?<!bzw)(?<!\d)(?<!\w\.\w)(?<=[.!?])\s+(?=[A-Z])', chunk)
        for sentence in sentences:
            sentence_chunks.append((sentence, context))

    return sentence_chunks


def split_chunks(text: str, chunk_size: int = 500) -> list:
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]



def store_in_faiss(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    embeddings = np.array(embeddings, dtype=np.float32)
    index.add(embeddings)
    return index


def create_index_v2(sections: dict) -> tuple:
    chunks = []

    for section_title, text in sections.items():
        section_chunks = PreProcessorOld.parse_paragraph(text)
        chunks.extend(section_chunks)

    # Load the Hugging Face model and tokenizer
    model_name = 'sentence-transformers/all-MiniLM-L6-v2'
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    # Create embeddings for the chunks
    embeddings = []
    for chunk in chunks:
        inputs = tokenizer(chunk, return_tensors='pt', padding=True, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
        embeddings.append(outputs.last_hidden_state[:,0,:].squeeze().cpu().numpy())

    embeddings = np.array(embeddings)

    # Create a FAISS index
    index = store_in_faiss(embeddings)

    return index, chunks, tokenizer, model

def create_index_v3(sections: dict) -> tuple:
    chunks = []

    for section_title, text in sections.items():
        section_chunks = paragraph_chunks_v3(text)
        chunks.extend(section_chunks)

    # Load the Hugging Face model and tokenizer
    model_name = 'sentence-transformers/all-MiniLM-L6-v2'
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    # Create embeddings for the chunks
    embeddings = []
    for chunk, _ in chunks:
        inputs = tokenizer(chunk, return_tensors='pt', padding=True, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
        embeddings.append(outputs.last_hidden_state[:,0,:].squeeze().cpu().numpy())

    embeddings = np.array(embeddings)

    # Create a FAISS index
    index = store_in_faiss(embeddings)

    return index, chunks, tokenizer, model

def search_index_v3(index, query, tokenizer, model, chunks, k=3):
    # Create an embedding for the query
    inputs = tokenizer(query, return_tensors='pt', padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    query_embedding = outputs.last_hidden_state[:, 0, :].squeeze().cpu().numpy()

    # Search the FAISS index for the k most similar chunks
    D, I = index.search(np.array([query_embedding]), k)
    results = [(chunks[i][0], chunks[i][1]) for i in I[0]]
    return results

def create_index(sections: dict) -> tuple:
    chunks = []

    for _, text in sections.items():
        section_chunks = PreProcessorOld.parse_paragraph(text)
        chunks.extend(section_chunks)
        # section_map.update({chunk: section_title for chunk in section_chunks})

    model = TfidfVectorizer()
    tfidf_matrix = model.fit_transform(chunks)
    tfidf_array = tfidf_matrix.toarray()

    index = store_in_faiss(tfidf_array)

    return index, chunks, model


def search_index_v2(index, query, tokenizer, model, chunks, k=3):
    # Create an embedding for the query
    inputs = tokenizer(query, return_tensors='pt', padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    query_embedding = outputs.last_hidden_state[:,0,:].squeeze().cpu().numpy()

    # Search the FAISS index for the k most similar chunks
    D, I = index.search(np.array([query_embedding]), k)
    results = [chunks[i] for i in I[0]]
    return results


def search_index(index, query, model, chunks, k=3):
    query_vec = model.transform([query]).toarray()
    _, I = index.search(query_vec, k)
    results = [chunks[i] for i in I[0]]
    return results