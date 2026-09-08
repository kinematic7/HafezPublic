import json
import chromadb
from typing import List, Optional

class HadithIngester:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(name="hadith_collection")

    def ingest_hadiths(self, hadith_data: Optional[List[dict]] = None):
        if hadith_data is None:
            files = ["sahih_bukhari.json", "sahih_muslim.json"]
            total_count = 0
            for file_path in files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        items = data.get("hadiths", data if isinstance(data, list) else [])
                        total_count += self._process_items(items)
                except FileNotFoundError:
                    print(f"Warning: '{file_path}' was not found.")
                except Exception as e:
                    print(f"Error loading '{file_path}': {str(e)}")
            return self.collection.count()
        else:
            self._process_items(hadith_data)
            return self.collection.count()

    def _process_items(self, items: List[dict]):
        ids, documents, metadatas = [], [], []
        for item in items:
            coll = item.get("collection", "Hadith")
            h_num = item.get("hadith_number")
            text = item.get("text")
            
            doc_id = f"{coll.lower().replace(' ', '_')}_{h_num}"
            document = f"Source: {coll} (Hadith {h_num}) | Text: {text}"
            
            ids.append(doc_id)
            documents.append(document)
            metadatas.append({"collection": coll, "hadith_number": h_num})
        
        # ChromaDB has a strict batch limit of 5461. Chunk data to prevent errors.
        batch_size = 5000
        for i in range(0, len(ids), batch_size):
            self.collection.upsert(
                ids=ids[i:i + batch_size],
                documents=documents[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size]
            )
        
        return len(ids)

    def query_hadiths(self, query: str, n_results: int = 3):
        if self.collection.count() == 0:
            return {"documents": [[]]}
        return self.collection.query(query_texts=[query], n_results=n_results)