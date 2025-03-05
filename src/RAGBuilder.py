class RAGBuilder:

    # altes embedding mit alter retriever klasse
    """
    embds = Retriever.create_embs(documents, "sentence-transformers/all-MiniLM-L12-v2")"nomic-ai/nomic-embed-text-v1"
    Retriever.create_embds_to_db(documents, "sentence-transformers/all-MiniLM-L12-v2", "src/db1")
    ol_embed = ollama.embed(model="all-minilm:33m",input=documents[0])
    print(ol_embed)
    print(embds)
    retr.create_embds_to_db(documents)
    """

    # altes embedding mit alter retriever klasse
    """
    embds = Retriever.create_embs(documents, "sentence-transformers/all-MiniLM-L12-v2")"nomic-ai/nomic-embed-text-v1"
    Retriever.create_embds_to_db(documents, "sentence-transformers/all-MiniLM-L12-v2", "src/db1")
    ol_embed = ollama.embed(model="all-minilm:33m",input=documents[0])
    print(ol_embed)
    print(embds)
    retr.create_embds_to_db(documents)
    """

    # parsing vom modulkatalog
    """
    modkat_raw = PDFLoader.ExtractTxtFromPyMuPDF("src/data/pdfs/MODKAT2019.pdf")
    FileHandler.saveStrToFile(modkat_raw, "src/data/modkat_raw_pymu.txt", "utf-8")
    """

    # creating docs and indexing them in db for retrieval paragraph chunks
    """
    sections = FileHandler.read_files("src/data/sections")
    documents = PreProcessorOld.paragraphs_chunks(sections)

    # retriever = RetrieverOLL("all-minilm:33m", "src/database/oll_minilm_1")
    retriever = RetrieverHF("sentence-transformers/all-MiniLM-L12-v2", "src/database/hf_minilm_1")
    retriever.create_embds_to_db(documents)
    """