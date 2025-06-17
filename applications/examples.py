from core import ComponentResultObject, settings
from api import Cro, VectorDB
from functions import ElevenlabsAudio, HuggingFaceReranker
from components import EmbeddingComponent, ChatComponent, PdfReaderComponent, ComparatorComponent
from agents import MRR
from os.path import join
from os import listdir


# pdf reader example
def components_pdfreadercomponent_retrieve(app_path):
    pdf_path = join(app_path, 'data\\pdf\\beispiel.pdf')
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

def components_comparator_invoke(app_path):
    comparator = ComparatorComponent()
    datas = []
    print("Prepraing data")
    with open(join(app_path, 'data\\txt\\ger.txt'), encoding="utf-8") as f:
        data_ger = f.readlines()
    with open(join(app_path, 'data\\txt\\eng.txt'), encoding="utf-8") as f:
        data_eng = f.readlines()
    if len(data_ger) != len(data_eng):
        raise TypeError("length mismatch")
    for i in range(len(data_eng)):
        if len(data_eng[i]) > 10:           
            data = ComponentResultObject()
            data["content"]["original_text"] = data_eng[i]
            data["preprocessing"]["result_text"] = data_ger[i]
            datas.append(data)
    print("Invoke ComparatorComponent")
    result = comparator.invoke(datas)
    with open(join(app_path, 'data\\txt\\res.txt'), "w", encoding="utf-8") as f:
        for res in result:            
            f.write("---\n")
            f.write(str(res["preprocessing"]["score"]))
            f.write("\n")
            f.write(res["preprocessing"]["summary"])
            f.write("\n\n")
            f.write(res["content"]["original_text"])
            f.write("\n")
            f.write(res["preprocessing"]["result_text"])
            f.write("\n")
            f.write("---\n\n")
    print("Finished")

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
    for token in __chatbot_stream__(provider=settings.ollama_model):
        print(token, end="")

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
    res = benchmark.run()
    print(f"MRR = {res}")

# pre- and postprocessing of user chat
# den user-query zunächst als "assistant" anfügen
# anschließend: "user": bitte prüfe deine vorherige aussage auf zweckentfremdung
# funktioniert ebenso für postprocessing: beinhaltet deine vorherige aussage sql injections etc.?
# code in plain text: https://blog.virustotal.com/2023/04/introducing-virustotal-code-insight.html

# streaming example using local llm and elevenlabs api (free tier)
def functions_elevenlabsaudio_invoke():
    audio = ElevenlabsAudio()
    audio.invoke("Hallo mein Lieber. Ich freue mich, von dir zu hören. Wie kann ich dir heute helfen?")


# websearch example
def components_websearchcomponent_invoke():
    from components import WebSearchComponent
    
    websearch = WebSearchComponent()
    
    # Create input with search query
    input_cro = ComponentResultObject()
    input_cro["content"]["original_text"] = "artificial intelligence latest developments 2025"
    input_cro["content"]["page_count"] = 3  # Get 3 search results
    
    results = websearch.invoke([input_cro])
    
    print(f"Found {len(results)} search results:")
    for result in results:
        print(f"\nRank: {result['retrieval']['rank']}")
        print(f"Title: {result['content']['title']}")
        print(f"URL: {result['source']}")
        print(f"Keywords: {result['preprocessing']['keywords']}")
        print(f"Publish Date: {result['content']['publish_date']}")
        print(f"Content preview: {result['content']['original_text'][:200]}...")

# dialectical reasoning example
def agents_dialecticalreasoning_invoke():
    from agents import DialecticalReasoningAgent
    
    reasoning_agent = DialecticalReasoningAgent()
    
    # Test the philosophical reasoning
    question = "Wird künstliche Intelligenz einmal so intelligent sein, dass sie den Menschen weit überlegen ist?"
    context = {"question": question}
    
    print(f"🧠 Starting dialectical reasoning for: {question}\n")
    
    result = reasoning_agent.run(context)
    
    print("=" * 80)
    print("📋 DIALECTICAL REASONING RESULT")
    print("=" * 80)
    print(f"Original Question: {result['original_question']}\n")
    
    print("🎯 THESE:")
    print(f"{result['these']}\n")
    
    print("🎯 ANTITHESE:")  
    print(f"{result['antithese']}\n")
    
    print("🔍 SEARCH TERMS:")
    print(f"These: {result['these_search_term']}")
    print(f"Antithese: {result['antithese_search_term']}\n")
    
    print("⚖️ ARGUMENTATION FÜR THESE:")
    print(f"{result['these_argumentation']}\n")
    
    print("⚖️ ARGUMENTATION FÜR ANTITHESE:")
    print(f"{result['antithese_argumentation']}\n")
    
    print("🎯 DIALECTICAL SYNTHESE:")
    print(f"{result['synthese']}\n")
    
    print("=" * 80)
