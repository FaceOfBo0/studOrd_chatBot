from Preprocessing import FileHandler, PreProcessorOld, PreProcessorNew
from Retrieval.RetrieverHF import RetrieverHF

def create_idx_hf_para(file_path: str, db_path: str, db_coll: str, model_name: str):
    # Creating docs and indexing them in db for retrieval paragraph chunks
    # minilm = sentence-transformers/all-MiniLM-L12-v2, e5 = danielheinz/e5-base-sts-en-de
    
    sections = FileHandler.read_files(file_path)
    documents = PreProcessorOld.paragraphs_chunks(sections)

    # retriever = RetrieverOLL("all-minilm:33m", "src/database/oll_minilm_1")
    retriever = RetrieverHF(model_name, db_path, "cuda")
    retriever.save_embds_to_db(documents, db_coll)


def create_idx_hf_sent(file_path: str, db_path: str, db_coll: str, model_name: str, sentctx_map_path: str):
    # creating docs and indexing them in db for retrieval sentence chunks
    #"src/database/hf_minilm", "src/data/studyReg.json"
    # minilm = sentence-transformers/all-MiniLM-L12-v2, e5 = danielheinz/e5-base-sts-en-de

    sentCtxMap = PreProcessorNew.create_sentence_context_map(sentctx_map_path)

    # retriever = RetrieverOLL("all-minilm:33m", "src/database/oll_minilm_1")
    retriever = RetrieverHF(model_name, db_path, "cuda")
    retriever.save_embds_to_db([item for item in sentCtxMap.keys()], db_coll)






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

# "src/data/sections", "src/database/hf_minilm_1","sentence-transformers/all-MiniLM-L12-v2"

# erstellen der studienOrdnung datenstruktur und speichern als JSON Datei
"""
regulation = PreProcessorNew.process_regulation()
for section in regulation.sections:
    print(f"Section {section.number}: {section.title}")

PreProcessorNew.save_to_json(regulation, "src/data/studyReg.json")
new = PreProcessorNew.load_from_json("src/data/studyReg.json")
for sec in new.sections:
    print(f"Section {sec.number}: {sec.title}")
"""


# Erstellen und printen der sentence-context map
"""
sentence_map = PreProcessorNew.create_sentence_context_map("src/data/studyReg.json")

# Example usage:
for sentence, context in sentence_map.items():
    context_str = PreProcessorNew.get_context_string(context)
    print(f"Sentence: {sentence}")
    print(f"Context: {context_str}")
    print("-" * 80)
"""

# test pipeline ohne web interface mit hardcoded query für paragraph chunks
"""
query = "Was sind die Voraussetzungen zur Zulassung zum Bachelorstudium Informatik gemäß § 8 der Studienordnung?"
retriever = RetrieverHF("sentence-transformers/all-MiniLM-L12-v2", "src/database/hf_minilm")
generator = Generator()

context = retriever.get_ctx_from_db(query, 2)
answer = generator.gen_response_oll("llama3.2:3b", query, context)

print("Kontext:\n")
for i, elem in enumerate(context):
    print (i+1,":",elem,"\n")

print("Antwort:\n")
print(answer,"\n")
"""

# test pipeline ohne web interface mit hardcoded query für sentence chunks
"""
query = "Was sind die Voraussetzungen zur Zulassung zum Bachelorstudium Informatik gemäß § 8 der Studienordnung?"
retriever = RetrieverHF("sentence-transformers/all-MiniLM-L12-v2", "src/database/hf_minilm")
generator = Generator()

context = retriever.get_ctx_from_db(query, 2)
answer = generator.gen_response_oll("llama3.2:3b", query, context)

print("Kontext:\n")
for i, elem in enumerate(context):
    print (i+1,":",elem,"\n")

print("Antwort:\n")
print(answer,"\n")
"""