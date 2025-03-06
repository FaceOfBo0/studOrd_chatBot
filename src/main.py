# from Preprocessing.PreProcessorNew import PreProcessorNew
# from Retrieval.RetrieverHF import RetrieverHF
# from Generation.Generator import Generator
# from Retrieval.RetrieverOLL import RetrieverOLL
# from Preprocessing import FileHandler, PreProcessorNew, PreProcessorOld
# from Preprocessing import PreProcessorNew
import RAGBuilder

if __name__ == '__main__':
    RAGBuilder.create_idx_hf_para("src/data/sections", "src/database/hf_e5", "docs_para", "danielheinz/e5-base-sts-en-de")
       