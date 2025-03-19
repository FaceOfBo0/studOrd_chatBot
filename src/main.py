# from Preprocessing.PreProcessorNew import PreProcessorNew
# from Retrieval.RetrieverHF import RetrieverHF
# from Generation.Generator import Generator
# from Retrieval.RetrieverOLL import RetrieverOLL
# from Preprocessing import FileHandler, PreProcessorNew, PreProcessorOld
# from Preprocessing import PreProcessor, FileHandler
# from spacy.language import Language
# import RAGBuilder

if __name__ == '__main__':
    # * RAGBuilder.create_idx_hf_pnt("src/data/json/sntCtxMap.json", "src/database/hf_dt_matryoshka", "docs_pnt", "akot/german-semantic-bmf-matryoshka")
    # * RAGBuilder.create_idx_hf_pnt("src/data/json/sntCtxMap.json", "src/database/hf_ml_jina_lora", "docs_pnt", "CISCai/jina-embeddings-v3-query-distilled")
    # ** RAGBuilder.create_idx_hf_para("src/data/sections", "src/database/hf_e5", "docs_para", "danielheinz/e5-base-sts-en-de")
    # **** AGBuilder.create_idx_hf_pnt("src/data/sntCtxMap.json", "src/database/hf_dt_gbert", "docs_pnt", "deutsche-telekom/gbert-large-paraphrase-cosine")

    # ***** RAGBuilder.create_idx_hf_pnt("src/data/json/sntCtxMap.json", "src/database/hf_ml_alibaba", "docs_pnt", "Alibaba-NLP/gte-multilingual-base")
    # ***** RAGBuilder.create_idx_hf_pnt("src/data/json/sntCtxMap.json", "docs_pnt", "jinaai/jina-embeddings-v3","src/database/hf_ml_jina_lora", "retrieval.passage")

    # study_reg = PreProcessor.process_regulation_wo_subpoints("src/data/sections")
    # FileHandler.save_regulation_to_json(study_reg, "src/data/json/stdReg_new.json")
    # pntCtxMap = PreProcessor.create_pntCtxMap_from_stdyReg(study_reg)

    # RAGBuilder.create_embds_hf_pnt("src/data/json/stdReg_new.json", "docs_pnt", "jinaai/jina-embeddings-v3", "src/database/hf_jinaai_lora_new", "retrieval.passage")


    ### Sentence Tokenizer and Table Parsing via spacy, spacy-layout

    # import pathlib
    #import spacy
    # import pandas as pd
    #from spacy_layout import spaCyLayout

    # model = spacy.load("de_core_news_md")
    # model = spacy.blank("de")
    # layout = spaCyLayout(model)

    # doc = layout("data/pdfs/MODKAT2019.pdf")

    #table = doc._.tables[10]
    #print(table.start, table.end, table._.layout)
    #print(table._.data)

    # i = 1
    # for ta in doc._.tables:
    #     if i < 10:
    #         ta._.data.to_pickle("data/modules/module0" + str(i)+".pkl")
    #     else:
    #         ta._.data.to_pickle("data/modules/module" + str(i)+".pkl")
    #     i += 1

    import pandas as pd

    frame = pd.read_pickle("data/modules/module11.pkl")
    print(frame)

    ## example of parsing sentences of one section (Abschnitt I) with spacy

    #@Language.component("custom_senter")
    #def custom_senter(doc):
     #   additional_delimiters = ["\n\n"]  # Add more delimiters as needed

        # Iterate through tokens and set sentence boundaries
    #    for token in doc:
    #        if token.text in additional_delimiters:
    #            doc[token.i + 1].is_sent_start = True
    #    return doc

    # model = spacy.load("de_core_news_md")
    # model.disable_pipe("parser")
    # model.enable_pipe("senter")
    #model.add_pipe("custom_senter", before="senter")

    # text = pathlib.Path("src/data/sections/Abschnitt II.txt").read_text(encoding="utf-8").replace("\n\n"," ").replace("\n"," ")
    # section_1_doc = model(text)
    # print([tok.text for tok in section_1_doc.sents])
