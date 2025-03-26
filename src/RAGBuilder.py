from Preprocessing import FileHandler, PreProcessor, PreProcessorOld
from Retrieval.RetrieverHF import RetrieverHF

def create_embds_hf_para(file_path: str, db_path: str, db_coll: str, model_name: str):
    # Creating docs and indexing them in db for retrieval paragraph chunks
    # minilm = sentence-transformers/all-MiniLM-L12-v2, e5 = danielheinz/e5-base-sts-en-de

    sections = FileHandler.read_section_files(file_path)
    documents = PreProcessorOld.paragraphs_chunks(sections)

    # retriever = RetrieverOLL("all-minilm:33m", "src/database/oll_minilm_1")
    retriever = RetrieverHF(model_name, db_path)
    retriever.save_embds_to_db(documents, db_coll)

def create_embds_hf_pnt(studyreg_path: str, db_coll: str, model: str, db: str = "", task: str = ""):
    studyReg = FileHandler.load_regulation_from_json(studyreg_path)
    pntCtxMap = PreProcessor.create_pntCtxMap_from_stdyReg(studyReg)

    ret = RetrieverHF(model_name=model, db_path=db, task_name=task)
    ret.save_embds_to_db([elem for elem in pntCtxMap.keys()], db_coll)

def create_embds_hf_sent(json_path: str, db_path: str, db_coll: str, model_name: str):
    # creating docs and indexing them in db for retrieval sentence chunks
    #"src/database/hf_minilm", "src/data/studyReg.json" "dict_sent"
    # minilm = sentence-transformers/all-MiniLM-L12-v2, e5 = danielheinz/e5-base-sts-en-de

    sentCtxMap = PreProcessor.create_sntCtxMap_list(json_path)

    # retriever = RetrieverOLL("all-minilm:33m", "src/database/oll_minilm_1")
    retriever = RetrieverHF(model_name, db_path, "cuda")
    retriever.save_embds_to_db([tpl[0] for tpl in sentCtxMap], db_coll)
