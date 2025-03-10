# from Preprocessing.PreProcessorNew import PreProcessorNew
# from Retrieval.RetrieverHF import RetrieverHF
# from Generation.Generator import Generator
# from Retrieval.RetrieverOLL import RetrieverOLL
# from Preprocessing import FileHandler, PreProcessorNew, PreProcessorOld
from Preprocessing import PreProcessor, FileHandler
import RAGBuilder
# import RAGBuilder

if __name__ == '__main__':
    # * RAGBuilder.create_idx_hf_pnt("src/data/json/sntCtxMap.json", "src/database/hf_dt_matryoshka", "docs_pnt", "akot/german-semantic-bmf-matryoshka")
    # * RAGBuilder.create_idx_hf_pnt("src/data/json/sntCtxMap.json", "src/database/hf_ml_jina_lora", "docs_pnt", "CISCai/jina-embeddings-v3-query-distilled")
    # ** RAGBuilder.create_idx_hf_para("src/data/sections", "src/database/hf_e5", "docs_para", "danielheinz/e5-base-sts-en-de")
    # **** AGBuilder.create_idx_hf_pnt("src/data/sntCtxMap.json", "src/database/hf_dt_gbert", "docs_pnt", "deutsche-telekom/gbert-large-paraphrase-cosine")

    # ***** RAGBuilder.create_idx_hf_pnt("src/data/json/sntCtxMap.json", "src/database/hf_ml_alibaba", "docs_pnt", "Alibaba-NLP/gte-multilingual-base")
    # ***** RAGBuilder.create_idx_hf_pnt("src/data/json/sntCtxMap.json", "docs_pnt", "jinaai/jina-embeddings-v3","src/database/hf_ml_jina_lora", "retrieval.passage")

    # study_reg = PreProcessor.process_regulation_without_subpoints("src/data/sections")
    # study_reg = FileHandler.load_regulation_from_json("src/data/json/stdReg.json")
    # pntCtxMap = PreProcessor.create_pntCtxMap_from_stdyReg(study_reg)

    RAGBuilder.create_embds_hf_pnt("src/data/json/stdRegPnts.json", "docs_pnt", "jinaai/jina-embeddings-v3", "src/database/hf_jinaai_lora", "retrieval.passage")