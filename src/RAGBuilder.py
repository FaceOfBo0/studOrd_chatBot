from Preprocessing import FileHandler, PreProcessor
from Retrieval.RetrieverHF import RetrieverHF

def create_embds_hf_modules(mods_path: str, db_coll: str, model: str, db_path: str = "", task: str = "", id_prefix: str = ""):
    """Create and save embeddings for module data using HuggingFace.
    
    Args:
        mods_path: Path to the directory containing module CSV files.
        db_coll: Name of the collection to save embeddings to.
        model: Name of the HuggingFace model to use.
        db_path: Optional path to persist the database. If empty, uses in-memory storage.
        task: Optional task name for task-specific embeddings.
        id_prefix: Optional prefix for document IDs in the database.
    """
    
    modules = PreProcessor.get_modules_from_csv(mods_path)

    retriever = RetrieverHF(model_name=model, db_path=db_path, task_name=task)
    retriever.save_embds_to_db([repr(mod) for mod in modules], db_coll, id_prefix)

def create_embds_hf_para(file_path: str, db_path: str, db_coll: str, model_name: str, id_prefix=""):
    """Create and save embeddings for paragraph chunks using HuggingFace.
    
    Args:
        file_path: Path to the directory containing section files.
        db_path: Path to persist the database.
        db_coll: Name of the collection to save embeddings to.
        model_name: Name of the HuggingFace model to use.
        id_prefix: Optional prefix for document IDs in the database.
    """
    
    sections = FileHandler.read_section_files(file_path)
    documents = PreProcessor.paragraphs_chunks(sections)

    retriever = RetrieverHF(model_name, db_path)
    retriever.save_embds_to_db(documents, db_coll, id_prefix)

def create_embds_hf_pnt(studyreg_path: str, db_coll: str, model: str, db: str = "", task: str = "", id_prefix: str = ""):
    """Create and save embeddings for study regulation points using HuggingFace.
    
    Args:
        studyreg_path: Path to the study regulation JSON file.
        db_coll: Name of the collection to save embeddings to.
        model: Name of the HuggingFace model to use.
        db: Optional path to persist the database. If empty, uses in-memory storage.
        task: Optional task name for task-specific embeddings.
        id_prefix: Optional prefix for document IDs in the database.
    """

    studyReg = FileHandler.load_regulation_from_json(studyreg_path)
    pntCtxMap = PreProcessor.create_pntCtxMap_from_stdyReg(studyReg)

    ret = RetrieverHF(model_name=model, db_path=db, task_name=task)
    ret.save_embds_to_db([elem for elem in pntCtxMap.keys()], db_coll, id_prefix)
