# quraningester.py
import json
import urllib.request
import chromadb
from typing import Any, Dict, List, Optional


class QuranIngester:

    def __init__(
        self,
        collection_name: str = "quran_knowledge_base",
        persist_directory: str = "./quran_chroma_db",
        embedding_function: Optional[Any] = None,
    ):
        """Initializes persistent ChromaDB client and collection for the Quran."""
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=embedding_function
        )

    def fetch_quran_dataset(self) -> List[Dict[str, Any]]:
        """Downloads complete Quran text (Arabic + English Sahih International)."""
        print("Fetching Quran dataset from API...")
        url = "https://cdn.jsdelivr.net/gh/fawaz-ahmed/quran-api@1/editions/eng-sahih.json"

        req = urllib.request.urlopen(url)
        data = json.loads(req.read().decode("utf-8"))
        return data["quran"]

    def ingest_quran(
        self,
        quran_data: Optional[List[Dict[str, Any]]] = None,
        batch_size: int = 500,
    ) -> int:
        """Processes and ingests all Ayahs into ChromaDB with metadata tags."""
        if quran_data is None:
            quran_data = self.fetch_quran_dataset()

        documents = []
        metadatas = []
        ids = []

        for item in quran_data:
            surah_num = item["chapter"]
            ayah_num = item["verse"]
            text_en = item["text"]

            # Deterministic unique ID for every verse (e.g. quran:2:255)
            doc_id = f"quran:{surah_num}:{ayah_num}"

            # Structured document text optimized for vector search
            formatted_document = f"Surah {surah_num}, Verse {ayah_num}: {text_en}"

            # Metadata for fast SQL-style filtering
            metadata = {
                "surah": int(surah_num),
                "ayah": int(ayah_num),
                "translation": "Sahih International",
            }

            documents.append(formatted_document)
            metadatas.append(metadata)
            ids.append(doc_id)

        # Batch write into ChromaDB
        total_items = len(documents)
        print(f"Ingesting {total_items} verses into collection '{self.collection_name}'...")

        for i in range(0, total_items, batch_size):
            self.collection.add(
                documents=documents[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
                ids=ids[i : i + batch_size],
            )

        print(f"Successfully ingested {self.collection.count()} total verses.")
        return self.collection.count()

    def query_quran(
        self,
        query: str,
        n_results: int = 3,
        surah_filter: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Performs semantic similarity search over stored Quran verses."""
        where_clause = {"surah": surah_filter} if surah_filter else None

        return self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause,
        )