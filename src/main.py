# from Retrieval.RetrieverHF import RetrieverHF
# from Generation.Generator import Generator
# from Retrieval.RetrieverOLL import RetrieverOLL
# from Preprocessing import FileHandler
# from Preprocessing import PreProcessor, FileHandler
# from spacy.language import Language
# import RAGBuilder
# import tabula

if __name__ == '__main__':
    pass
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


### create embeds for modules
    # RAGBuilder.create_embds_hf_modules("data/modules/tabula csv/B und WPF", "docs_pnt", "jinaai/jina-embeddings-v3", "database/hf_jinaai_lora", "retrieval.passage")

    # retr = RetrieverHF("jinaai/jina-embeddings-v3", "database/hf_jinaai_lora_new", "retrieval.query")
    # result = retr.get_results_from_db("Wieviel CP hat das Modul Lineare Algebra und Diskrete Mathematik?", 3, "docs_mods")
    # print(result)


### use tabula for table extraction from modules pdfs

    # tables = tabula.io.read_pdf("src/data/pdfs/MODKAT2019.pdf", pages="15-91", multiple_tables=True)
    # if isinstance(tables, list):
    #     elem = tables[4]
    #     if not elem.empty:
    #        print(elem.to_numpy())


### regex for pattern matching of title and short_title in Module

    # import Preprocessing.FileHandler as fh

    # lst_mods = fh.parse_modules_from_csv("data/modules/tabula csv/B und WPF")
    #
    # pattern = r'^([A-Z]+(?:-[A-Za-z0-9]+)*)([A-ZÄÖÜ][a-z][\w -/().]+)$'
    # pattern = r'^([A-Z]+(?:-[A-Za-z0-9]+)*)([A-ZÄÖÜ].*)$'
    # pattern = r'^(B-NLP-DS|[A-Z]+(?:-[A-Za-z0-9]+)*)([A-ZÄÖÜ].*)$'
    # for i, m in enumerate(lst_mods):
        # match = re.match(pattern, m.title)
        # if match:
        #     abkuerzung = match.group(1)
        #     titel = match.group(2).strip()
        #     print(f"Abkürzung: {abkuerzung}, Titel: {titel}")
        # else:
        #     print(f"Kein Treffer für: {m.title}")

### import csv

    # with open("src/data/modules/csv tabula/tabula-MODKAT2019-7.csv", mode="r") as file:
    #    csv_file = csv.reader(file)
    #     for line in csv_file:
    #         print(line)

    # serialize/deserialize py Object to JSON with jsonpickle

    # import jsonpickle as jp
    # import json
    # with open("data/modules/csv tabula/tabula-MODKAT2019-10.csv") as file:
    #     mod = Module(file)
    #     modJSON = jp.encode(mod, unpicklable=True)

    # with open("data/modules/test.json", "w", encoding="utf-8") as f:
    #     json.dump(modJSON, f, indent=4)
    # mod_obj = jp.decode(modJSON)
    # print(mod_obj)


### Table Parsing via spacy-layout

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

    # import pandas as pd
    # from pandas import DataFrame

    # frame = DataFrame(pd.read_pickle("src/data/modules/module08.pkl"))
    # np_frame = frame.to_numpy()
    # print(np_frame)


### example of parsing sentences of one section (Abschnitt I) with spacy

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
