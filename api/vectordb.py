import chromadb
from typing import Any, Dict, List
from core import ComponentResultObject
from api import BaseApi
from globals import Globals


class VectorDB(BaseApi):
    client_path: str
    client_collection: str

    #read compares cro (standard and enhanced embedding) with vectordb
    def retrieve(self, input:List[ComponentResultObject])->List[ComponentResultObject]:
        client = chromadb.PersistentClient(path=self.client_path)
        try:
           collections = [
               client.get_collection(name=f"{self.client_collection}_standard"),
               client.get_collection(name=f"{self.client_collection}_enhanced"),
            ]
        except:
            raise KeyError("VectorDB API: Collection does not exist.")
        
        results = []
        for data in input:
            for embedding in [
                data["preprocessing"]["embedding"]["standard"],
                data["preprocessing"]["embedding"]["enhanced"]
            ]:
                if embedding is not None:
                    ranking = collections[0].query(
                                query_embeddings=[embedding],
                                n_results=Globals.max_vectordb_results
                            )
                    for i in range(len(ranking["ids"][0])):
                        results.append(self.__create_cro_from_vectordb_entry(
                            ranking["ids"][0][i], 
                            i,
                            ranking["distances"][0][i],
                            ranking["metadatas"][0][i]
                        ))
        
        return results
            
    def write(self, output:List[ComponentResultObject]):
        client = chromadb.PersistentClient(path=self.client_path)
        collections = [
            self.__get_collection__(
                client=client, 
                collection_name=f"{self.client_collection}_standard"),
            self.__get_collection__(
                client=client, 
                collection_name=f"{self.client_collection}_enhanced"),
        ]
        ids = [d["unique_id"] for d in output]
        embeddings = [
            [d["preprocessing"]["embedding"]["standard"] for d in output],
            [d["preprocessing"]["embedding"]["enhanced"] for d in output]
        ]
        metadatas = [
            {
                "source": self.__check_for_none__(d["source"]),
                "page_number": self.__check_for_none__(d["content"]["page_number"]),
                "original_text": self.__check_for_none__(d["content"]["original_text"]),
                "result_text": self.__check_for_none__(d["preprocessing"]["result_text"]),
                "summary": self.__check_for_none__(d["preprocessing"]["summary"]),
                "keywords": self.__check_for_none__(d["preprocessing"]["keywords"])
            } for d in output]

        for i in range(2):
            if embeddings[i][0] is not None:
                collections[i].upsert(
                    embeddings=embeddings[i],
                    metadatas=metadatas,
                    ids=ids
                )

    def get_all(self)->List[ComponentResultObject]:
        client = chromadb.PersistentClient(path=self.client_path)
        try:
           collections = [
               client.get_collection(name=f"{self.client_collection}_standard"),
               client.get_collection(name=f"{self.client_collection}_enhanced"),
            ]
        except:
            raise KeyError("VectorDB API: Collection does not exist.")
        
        results = []
        datas = collections[0].get()
        for i in range(len(datas["ids"])):
            results.append(self.__create_cro_from_vectordb_entry(
                datas["ids"][i], 
                i,
                None,
                datas["metadatas"][i]
            ))

        return results

    def __get_collection__(self, client:chromadb.PersistentClient, collection_name:str)->chromadb.Collection:
        return client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:batch_size":10000} #erforderlich da chroma sonst bei mehr als 100 einträgen (silent) crash
        )
    
    def __check_for_none__(self, value:str)->str:
        if value is None:
            return ""
        else:
            return value

    def __create_cro_from_vectordb_entry(self, id:str, rank:int, d:float, md:Dict[str, Any])->ComponentResultObject:
        cro = ComponentResultObject()
        cro["unique_id"] = id
        cro["source"] = md["source"]
        cro["content"]["original_text"] = md["original_text"]
        cro["content"]["page_number"] = md["page_number"]
        cro["preprocessing"]["result_text"] = md["result_text"]
        cro["preprocessing"]["summary"] = md["summary"]
        cro["preprocessing"]["keywords"] = md["keywords"]
        cro["retrieval"]["rank"] = rank + 1
        cro["retrieval"]["distance"] = d
        return cro
