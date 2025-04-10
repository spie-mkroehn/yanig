from dotenv import load_dotenv
from os.path import join, dirname
from applications import examples


if __name__=="__main__":
    app_path = dirname(__file__)
    load_dotenv(join(app_path, '.env'))

    #read pdfs
    examples.components_pdfreadercomponent_retrieve(app_path)

    #generate standard embeddings from examples and write to json
    #examples.components_embeddingcomponent_api_cro_write(app_path)

    #read some cro data and write to chromadb
    #examples.api_cro_read_api_vectordb_write(app_path)

    #semantic search
    #examples.components_embeddingcomponent_api_vektordb_read(app_path)

    #reranker
    #examples.components_rerankercomponent(app_path)

    #simple chat
    #examples.components_chatcomponent()

    #mrr
    #examples.agents_mrr_invoke(app_path)

    #elevenlabsaudio
    #examples.functions_elevenlabsaudio_invoke()
    #examples.functions_elevenlabsaudio_stream()
