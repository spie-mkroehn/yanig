from core import ComponentResultObject
from api import Cro, VectorDB
from functions import ElevenlabsAudio, HuggingFaceReranker
from components import EmbeddingComponent, ChatComponent, PdfReaderComponent
from agents import MRR
from os.path import join
from os import listdir


# pdf reader example
def components_pdfreadercomponent_retrieve(app_path):
    pdf_path = join(app_path, 'data\\pdf\\beispiel.pdf')
    json_path = join(app_path, 'data\\json\\beispiel\\')

    chatbot = ChatComponent()
    pdfreader = PdfReaderComponent()

    input = ComponentResultObject()
    input["source"] = pdf_path
    input["content"]["page_number"] = 1
    input["content"]["page_count"] = 1
    results = pdfreader.invoke([input])

    for result in results:
        print(result["content"]["chapter"], result["content"]["page_number"])
        print(result["content"]["original_text"])

# read example text, calculate embeddings for paragraphs and write to json files
def components_embeddingcomponent_api_cro_write(app_path):
    ec = EmbeddingComponent()
    cro_api = Cro()

    txt_path = join(app_path, 'data\\txt\\example.txt')
    json_path = join(app_path, 'data\\json\\wiki')

    infos = []
    with open(txt_path, "r", encoding="utf-8") as f:
        info = None
        for l in f.readlines():
            if '#' in l:
                if info is not None:
                    infos.append(info)
                info = ComponentResultObject()
                info["preprocessing"]["category"] = l[2:-1]
                info["source"] = f"{l[2:-1]}.json"
                info["target"] = join(json_path, f"{l[2:-1]}.json")
                info["content"]["original_text"] = ""
            else:
                info["content"]["original_text"] += l
    
    infos = ec.invoke(infos)
    cro_api.write(infos)    

# read json files and store content in chroma db   
def api_cro_read_api_vectordb_write(app_path):
    cro_api = Cro()
    vdb = VectorDB(
        client_path=join(app_path, 'data\\db\\wiki'),
        client_collection="wiki"
    )

    #gather some data
    json_path = join(app_path, 'data\\json\\wiki')
    json_files = []
    filenames = [f for f in listdir(json_path) if f.endswith(".json")]
    for filename in filenames:
        cro_data = ComponentResultObject()
        cro_data["source"] = join(json_path, filename)
        json_files.append(cro_data)
    results = cro_api.retrieve(json_files)

    vdb.write(results)

# semantic search example
def components_embeddingcomponent_api_vektordb_read(app_path):
    ec = EmbeddingComponent()
    vdb = VectorDB(
        client_path=join(app_path, 'data\\db\\wiki'),
        client_collection="wiki"
    )
    question = ComponentResultObject()
    question["content"]["original_text"] = "Welche neuen Technologien gibt es, die Menschen unterstützen?"

    question = ec.invoke([question])[0]
    matches = vdb.retrieve([question])

    for match in matches:
        print(match["retrieval"]["distance"],
              match["content"]["original_text"])

# reranker example
def components_rerankercomponent(app_path):
    reranker = HuggingFaceReranker()
    # get all entries from db
    vdb = VectorDB(
        client_path=join(app_path, 'data\\db\\wiki'),
        client_collection="wiki"
    )    
    data = vdb.get_all()
    print("Original:")
    for i in range(3):
        print(data[i]["content"]["original_text"])
    print("---")
    # rerank based on query
    query = "Welche Rolle spielen Roboter in der Fabrik der Zukunft?"
    results = reranker.invoke(query, data)
    print("Reranked:")
    for i in range(3):
        print(results[i]["content"]["original_text"])

# simple chat-example (streaming)
def components_chatcomponent():
    for token in __chatbot_stream__():
        print(token["message"]["content"], end="")

def __chatbot_stream__(
    system_text: str = """
        Du bist ein Nobelpreisträger für Physik, der auf dem Gebiet der Kosmologie schwarzer Löcher forscht.
        Du beantwortest Fragen zu diesem Thema auf einem hohen wissenschaftlichen Niveau.
    """,
    user_text: str = """
        Wie hoch sind die Gezeitenkräfte bei Überschreiten des Ereignishorizonts eines supermassiven Schwarzen Lochs?
    """,
    provider: str = "ollama"):
    chatbot = ChatComponent()

    system_prompt = ComponentResultObject()
    system_prompt["source"] = "system"
    system_prompt["content"]["original_text"] = system_text
    user_prompt = ComponentResultObject()
    user_prompt["source"] = "user"
    user_prompt["content"]["original_text"] = user_text

    for token in chatbot.stream([system_prompt, user_prompt]):
        if token is not None:
            if "ollama" in provider:
                yield token["message"]["content"]
            elif "openai" in provider:
                yield token.choices[0].delta.content
        #print("Generator exhausted!")

# linear agent that calculates mean reciprocal rank
def agents_mrr_invoke(app_path):
    benchmark = MRR(dbpath=join(app_path, 'data\\db\\wiki'))
    res = benchmark.invoke()
    print(f"MRR = {res}")

# streaming example using local llm and elevenlabs api (free tier)
def functions_elevenlabsaudio_invoke():
    audio = ElevenlabsAudio()
    audio.invoke("Hallo mein Lieber. Ich freue mich, von dir zu hören. Wie kann ich dir heute helfen?")

def functions_elevenlabsaudio_stream():
    audio = ElevenlabsAudio()
    user_input = None
    while(True):
        user_input = input(">")
        audio.stream(__chatbot_stream__(
            system_text="""
                Dein Name ist Lea. Du bist ein hilfreiches Assistenzsystem.
                Du unterstützt bei Recherchen zu wissenschaftlichen und technischen Themen.
                Du bist freundlich und gelegentlich sarkastisch und schnippisch.
            """,
            user_text=user_input
        ))
