from Preprocessing.PreProcessorNew import PreProcessorNew
# from Retrieval.RetrieverHF import RetrieverHF
# from Generation.Generator import Generator
# from Retrieval.RetrieverOLL import RetrieverOLL
# from Preprocessing import FileHandler, PDFLoader, PreProcessor

if __name__ == '__main__':
    # sections = FileHandler.read_files("src/data/sections")
    # documents = PreProcessor.sections_chunks(sections)

    # regulation = PreProcessorNew.process_regulation()
    # for section in regulation.sections:
    #   print(f"Section {section.number}: {section.title}")
    
    # preProc.save_to_json(regulation, "src/data/studyReg.json")
    # new = PreProcessorNew.load_from_json("src/data/studyReg.json")
    # for sec in new.sections:
    #     print(f"Section {sec.number}: {sec.title}")


# Create the sentence-context map
    sentence_map = PreProcessorNew.create_sentence_context_map("src/data/studyReg.json")

# Example usage:
    for sentence, context in sentence_map.items():
        context_str = PreProcessorNew.get_context_string(context)
        print(f"Sentence: {sentence}")
        print(f"Context: {context_str}")
        print("-" * 80)


    # query = "Was sind die Voraussetzungen zur Zulassung zum Bachelorstudium Informatik gemäß § 8 der Studienordnung?"
    # retriever = RetrieverHF("sentence-transformers/all-MiniLM-L12-v2", "src/database/hf_minilm")
    # generator = Generator()

    # context = retriever.get_ctx_from_db(query, 2)
    # answer = generator.gen_response_oll("llama3.2:3b", query, context)

    # print("Kontext:\n")
    # for i, elem in enumerate(context):
    #     print (i+1,":",elem,"\n")

    # print("Antwort:\n")
    # print(answer,"\n")

































    # embds = Retriever.create_embs(documents, "sentence-transformers/all-MiniLM-L12-v2")"nomic-ai/nomic-embed-text-v1"
    # Retriever.create_embds_to_db(documents, "sentence-transformers/all-MiniLM-L12-v2", "src/db1")
    # ol_embed = ollama.embed(model="all-minilm:33m",input=documents[0])
    # print(ol_embed)
    # print(embds)
    # retr.create_embds_to_db(documents)

    # modkat_raw = PDFLoader.ExtractTxtFromPyMuPDF("src/data/pdfs/MODKAT2019.pdf")
    # FileHandler.saveStrToFile(modkat_raw, "src/data/modkat_raw_pymu.txt", "utf-8")

    # retriever = RetrieverOLL("all-minilm:33m")
    # retriever.create_embds_to_db(documents)
