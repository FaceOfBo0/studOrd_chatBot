from click import File
from Retrieval import Indexer_old
from Preprocessing import FileHandler
from Generation import Generator_old
from huggingface_hub import login

if __name__ == '__main__':

    sections = FileHandler.read_files("src/data/sections")
    idx, chks, tok, model = Indexer_old.create_index(sections)

    query = "Kann ich mich in ein höheres Fachsemester einschreiben?"
    retrieval = Indexer_old.search_index(idx, query, model, chks, 3)
    contexts = [result for result in retrieval]

    generator = Generator_old.Generator()
    # response = generator.gen_resp_deepseek(query, contexts)
    # response = generator.gen_resp_pipeline("Qwen/Qwen2.5-1.5B-Instruct-GPTQ-Int8", query, contexts)
    response = generator.gen_resp_pipeline("Qwen/Qwen2.5-3B-Instruct", query, contexts)
    # response = generator.gen_resp_janus_pro(query, contexts)
    
    print("\nQuery:", query)
    print("\nRelevant contexts:")
    for i, result in enumerate(retrieval):
        print(f"\n{i+1}.", result)
    print("\nGenerated response:", response)



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # text = PDFLoader.ExtractTxtFromPDFPlumber("src/pdfs/SOINF2019.pdf", [x + 1 for x in range(43) if x > 4])
    # text = PDFLoader.ExtractTxtFromPyMuPDF("src/pdfs/SOINF2019.pdf")
    # PDFLoader.saveStrToFile(text, "src/data/rawTextSO.txt", 'utf-8')
    # PreProcessor.split_sections("src/data/rawTextSO.txt")
    # idx, chks, tokenizer, model = Indexer.create_index_v3(sections)
    # results = Indexer.search_index_v3(idx, query, tokenizer, model, chks, 5)
    #for i, result in enumerate(results):
    #    print(i, result)