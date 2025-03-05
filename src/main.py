# from Preprocessing.PreProcessorNew import PreProcessorNew
from Retrieval.RetrieverHF import RetrieverHF
# from Generation.Generator import Generator
# from Retrieval.RetrieverOLL import RetrieverOLL
# from Preprocessing import FileHandler, PreProcessorNew, PreProcessorOld
from Preprocessing.PreProcessorNew import PreProcessorNew

if __name__ == '__main__':
    
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

    # creating docs and indexing them in db for retrieval paragraph chunks
    # sentCtxMap = PreProcessorNew.create_sentence_context_map("src/data/studyReg.json")
    
    # retriever = RetrieverOLL("all-minilm:33m", "src/database/oll_minilm_1")
    retriever = RetrieverHF("sentence-transformers/all-MiniLM-L12-v2", "src/database/hf_minilm")
    # retriever.save_embds_to_db_sent([item for item in sentCtxMap.keys()])
    results_retr = retriever.get_ctx_from_db_sent("Ist ein Auslandssemester möglich?", 3)
    print(results_retr)