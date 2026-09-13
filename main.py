import json
import re
from typing import Dict, List, Optional, Tuple
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from chatbot import ChatBot
from quraningester import QuranIngester
from hadithingester import HadithIngester

# Initialize FastAPI App
app = FastAPI(
    title="Quran & Hadith Search & RAG ChatBot API",
    description="API for ingesting, clearing, and querying Quranic verses and Sahih Hadiths with LangGraph ChatBot responses.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production to match your specific frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize persistent singletons
ingester = QuranIngester()
hadith_ingester = HadithIngester()
chatbot = ChatBot()

# --- In-Memory Hash Maps ---
TRANSLITERATION_MAP: Dict[Tuple[int, int], str] = {}
ARABIC_MAP: Dict[Tuple[int, int], str] = {}
TRANSLATION_MAP: Dict[Tuple[int, int], str] = {}

# Surah Names mapping (1-114) for fuzzy query parsing
SURAH_NAMES: Dict[str, int] = {
    "fatiha": 1, "al-fatiha": 1, "alfatiha": 1, "opening": 1,
    "baqarah": 2, "al-baqarah": 2, "albaqarah": 2, "cow": 2,
    "imran": 3, "ali 'imran": 3, "ali imran": 3, "al-imran": 3,
    "an-nisa": 4, "nisa": 4, "women": 4,
    "al-maidah": 5, "maidah": 5, "table": 5,
    "al-an'am": 6, "anam": 6, "cattle": 6,
    "al-a'raf": 7, "araf": 7,
    "al-anfal": 8, "anfal": 8,
    "at-tawbah": 9, "tawbah": 9, "repentance": 9,
    "yunus": 10, "yunas": 10,
    "hud": 11,
    "yusuf": 12, "joseph": 12,
    "ar-ra'd": 13, "rad": 13, "thunder": 13,
    "ibrahim": 14, "abraham": 14,
    "al-hijr": 15, "hijr": 15,
    "an-nahl": 16, "nahl": 16, "bee": 16,
    "al-isra": 17, "isra": 17,
    "kahf": 18, "al-kahf": 18, "cave": 18,
    "maryam": 19, "mary": 19,
    "taha": 20, "ta-ha": 20,
    "al-anbiya": 21, "anbiya": 21, "prophets": 21,
    "al-hajj": 22, "hajj": 22, "pilgrimage": 22,
    "al-mu'minun": 23, "muminun": 23,
    "an-nur": 24, "nur": 24, "light": 24,
    "al-furqan": 25, "furqan": 25,
    "ash-shu'ara": 26, "shuara": 26, "poets": 26,
    "an-naml": 27, "naml": 27, "ant": 27,
    "al-qasas": 28, "qasas": 28,
    "al-ankabut": 29, "ankabut": 29, "spider": 29,
    "ar-rum": 30, "rum": 30, "romans": 30,
    "luqman": 31,
    "as-sajdah": 32, "sajdah": 32, "prostration": 32,
    "al-ahzab": 33, "ahzab": 33,
    "saba": 34, "sheba": 34,
    "fatir": 35,
    "yasin": 36, "ya-sin": 36, "yaseen": 36,
    "as-saffat": 37, "saffat": 37,
    "sad": 38,
    "az-zumar": 39, "zumar": 39,
    "ghafir": 40, "mumin": 40,
    "fussilat": 41,
    "ash-shura": 42, "shura": 42,
    "az-zukhruf": 43, "zukhruf": 43,
    "ad-dukhan": 44, "dukhan": 44, "smoke": 44,
    "al-jathiyah": 45, "jathiyah": 45,
    "al-ahqaf": 46, "ahqaf": 46,
    "muhammad": 47,
    "al-fath": 48, "fath": 48, "victory": 48,
    "al-hujurat": 49, "hujurat": 49,
    "qaf": 50,
    "adh-dhariyat": 51, "dhariyat": 51,
    "at-tur": 52, "tur": 52,
    "an-najm": 53, "najm": 53, "star": 53,
    "al-qamar": 54, "qamar": 54, "moon": 54,
    "ar-rahman": 55, "rahman": 55,
    "al-waqi'ah": 56, "waqiah": 56,
    "al-hadid": 57, "hadid": 57, "iron": 57,
    "al-mujadila": 58, "mujadila": 58,
    "al-hashr": 59, "hashr": 59,
    "al-mumtahanah": 60, "mumtahanah": 60,
    "as-saff": 61, "saff": 61,
    "al-jumu'ah": 62, "jumuah": 62, "friday": 62,
    "al-munafiqun": 63, "munafiqun": 63,
    "at-taghabun": 64, "taghabun": 64,
    "at-talaq": 65, "talaq": 65, "divorce": 65,
    "at-tahrim": 66, "tahrim": 66,
    "al-mulk": 67, "mulk": 67, "sovereignty": 67,
    "al-qalam": 68, "qalam": 68, "pen": 68,
    "al-haqqah": 69, "haqqah": 69,
    "al-ma'arij": 70, "maarij": 70,
    "nuh": 71, "noah": 71,
    "al-jinn": 72, "jinn": 72,
    "al-muzzammil": 73, "muzzammil": 73,
    "al-muddaththir": 74, "muddaththir": 74,
    "al-qiyamah": 75, "qiyamah": 75, "resurrection": 75,
    "al-insan": 76, "insan": 76,
    "al-mursalat": 77, "mursalat": 77,
    "an-naba": 78, "naba": 78,
    "an-nazi'at": 79, "naziat": 79,
    "abasa": 80,
    "at-takwir": 81, "takwir": 81,
    "al-infitar": 82, "infitar": 82,
    "al-mutaffifin": 83, "mutaffifin": 83,
    "al-inshiqaq": 84, "inshiqaq": 84,
    "al-buruj": 85, "buruj": 85,
    "at-tariq": 86, "tariq": 86,
    "al-a'la": 87, "ala": 87,
    "al-ghashiyah": 88, "ghashiyah": 88,
    "al-fajr": 89, "fajr": 89, "dawn": 89,
    "al-balad": 90, "balad": 90, "city": 90,
    "ash-shams": 91, "shams": 91, "sun": 91,
    "al-layl": 92, "layl": 92, "night": 92,
    "ad-duha": 93, "duha": 93,
    "ash-sharh": 94, "sharh": 94, "inshirah": 94,
    "at-tin": 95, "tin": 95, "fig": 95,
    "al-alaq": 96, "alaq": 96,
    "al-qadr": 97, "qadr": 97,
    "al-bayyinah": 98, "bayyinah": 98,
    "az-zalzalah": 99, "zalzalah": 99, "zilzal": 99,
    "al-adiyat": 100, "adiyat": 100,
    "al-qari'ah": 101, "qariah": 101,
    "at-takathur": 102, "takathur": 102,
    "al-asr": 103, "asr": 103,
    "al-humazah": 104, "humazah": 104,
    "al-fil": 105, "fil": 105, "elephant": 105,
    "quraysh": 106,
    "al-ma'un": 107, "maun": 107,
    "al-kawthar": 108, "kawthar": 108, "kauthar": 108,
    "al-kafirun": 109, "kafirun": 109,
    "an-nasr": 110, "nasr": 110,
    "al-masad": 111, "masad": 111, "lahab": 111,
    "al-ikhlas": 112, "ikhlas": 112,
    "al-falaq": 113, "falaq": 113,
    "an-nas": 114, "nas": 114,
}


def load_json_dataset(file_paths: List[str], target_map: Dict[Tuple[int, int], str], label: str):
    """Helper to load dataset JSON files into a (chapter, verse) hash map."""
    file_found = False
    for path in file_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                items = data.get("quran_data", data if isinstance(data, list) else [])
                for item in items:
                    key = (int(item["chapter"]), int(item["verse"]))
                    target_map[key] = item["text"]
            print(f"Loaded {len(target_map)} {label} verses from '{path}'.")
            file_found = True
            break
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error loading '{path}': {str(e)}")
            break

    if not file_found:
        print(f"Warning: None of {file_paths} were found. {label.capitalize()} lookups will return default notices.")


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data"

@app.on_event("startup")
def load_datasets():
    """Loads translation, transliteration, and Arabic JSON datasets into O(1) hash maps on app startup."""
    load_json_dataset([str(DATA_DIR / "transliteration.json"), str(DATA_DIR / "quran_transliteration.json")], TRANSLITERATION_MAP, "transliteration")
    load_json_dataset([str(DATA_DIR / "arabic.json"), str(DATA_DIR / "quran_arabic.json")], ARABIC_MAP, "Arabic")
    load_json_dataset([str(DATA_DIR / "translation.json"), str(DATA_DIR / "quran_translation.json"), str(DATA_DIR / "quran.json")], TRANSLATION_MAP, "translation")

def detect_full_surah_request(query: str) -> Optional[Tuple[int, str]]:
    """
    Detects if a prompt is asking for an entire Surah's text, translation, or transliteration.
    Returns (surah_number, mode) where mode is 'translation', 'transliteration', or 'arabic'.
    """
    cleaned_query = query.lower().strip()

    requested_mode = "translation"  # Default
    if "transliteration" in cleaned_query:
        requested_mode = "transliteration"
    elif "arabic" in cleaned_query:
        requested_mode = "arabic"
    elif "translation" in cleaned_query or "translate" in cleaned_query or "english" in cleaned_query:
        requested_mode = "translation"

    surah_digit_match = re.search(r"(?:surah|chapter|soorah)\s+(\d{1,3})", cleaned_query)
    if surah_digit_match:
        surah_num = int(surah_digit_match.group(1))
        if 1 <= surah_num <= 114:
            return surah_num, requested_mode

    for name, number in SURAH_NAMES.items():
        pattern = r"\b" + re.escape(name) + r"\b"
        if re.search(pattern, cleaned_query):
            if any(k in cleaned_query for k in ["give", "show", "get", "read", "translation", "transliteration", "arabic", "text", "surah", "chapter"]):
                return number, requested_mode

    return None


def fetch_entire_surah(surah_num: int) -> Tuple[List[dict], List[dict], List[dict]]:
    """Extracts all verses for a given Surah across translation, transliteration, and Arabic maps."""
    translations, transliterations, arabics = [], [], []
    verse_num = 1

    while True:
        key = (surah_num, verse_num)
        has_data = False

        if key in TRANSLATION_MAP or key in ARABIC_MAP or key in TRANSLITERATION_MAP:
            has_data = True

            translations.append({
                "surah": surah_num,
                "verse": verse_num,
                "translation": TRANSLATION_MAP.get(key, "Translation not available")
            })

            transliterations.append({
                "surah": surah_num,
                "verse": verse_num,
                "transliteration": TRANSLITERATION_MAP.get(key, "Transliteration not available")
            })

            arabics.append({
                "surah": surah_num,
                "verse": verse_num,
                "text_arabic": ARABIC_MAP.get(key, "Arabic text not available")
            })

            verse_num += 1
        else:
            if not has_data:
                break

    return translations, transliterations, arabics


def parse_surah_verse(text: str) -> Optional[Tuple[int, int]]:
    """Extracts (chapter, verse) from strings like 'Surah 18, Verse 75: [Al-Khidr]...'"""
    match = re.search(r"Surah\s+(\d+),\s*Verse\s+(\d+)", text, re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None


def extract_clean_translation(text: str) -> str:
    """Strips out the 'Surah X, Verse Y: ' header from document string."""
    if ":" in text:
        return text.split(":", 1)[1].strip()
    return text.strip()


# --- Pydantic Request & Response Models ---

class QueryRequest(BaseModel):
    query: str = Field(..., examples=["What does the Quran say about patience?"])
    n_results: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of context items to retrieve",
    )
    surah_filter: Optional[int] = Field(
        default=None, description="Optional Surah number (1-114)"
    )
    source_type: str = Field(
        default="both", description="Target corpus: 'quran', 'hadith', or 'both'"
    )


class VerseItem(BaseModel):
    chapter: int = Field(..., examples=[1])
    verse: int = Field(..., examples=[1])
    text: str = Field(
        ...,
        examples=[
            "In the name of Allah, the Entirely Merciful, the Especially Merciful."
        ],
    )


class CustomIngestRequest(BaseModel):
    quran_data: Optional[List[VerseItem]] = Field(
        default=None,
        description="Optional list of custom verse objects to ingest. Omit to trigger automated download.",
    )


# --- API Endpoints ---

@app.post("/ingest", tags=["Quran Ingestion"])
def ingest_quran_endpoint(
    request: Optional[CustomIngestRequest] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    raw_data = None

    if request and request.quran_data:
        raw_data = [
            {"chapter": item.chapter, "verse": item.verse, "text": item.text}
            for item in request.quran_data
        ]

    if raw_data:
        count = ingester.ingest_quran(quran_data=raw_data)
        return {
            "status": "success",
            "message": f"Successfully ingested {len(raw_data)} verse(s) into ChromaDB.",
            "total_verses_in_db": count,
        }
    else:
        background_tasks.add_task(ingester.ingest_quran)
        return {
            "status": "processing",
            "message": "Full Quran ingestion task started in the background.",
        }


@app.post("/ingest/hadith", tags=["Hadith Ingestion"])
def ingest_hadith_endpoint(background_tasks: BackgroundTasks = BackgroundTasks()):
    background_tasks.add_task(hadith_ingester.ingest_hadiths)
    return {
        "status": "processing",
        "message": "Sahih al-Bukhari and Sahih Muslim background ingestion task started.",
    }


@app.post("/ingest/file", tags=["Quran Ingestion"])
async def ingest_quran_file_endpoint(
    file: UploadFile = File(
        ..., description="Upload a JSON dataset file (e.g., quran_dataset.json)"
    ),
):
    try:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))

        if isinstance(data, dict) and "quran_data" in data:
            raw_data = data["quran_data"]
        elif isinstance(data, list):
            raw_data = data
        else:
            raise ValueError("JSON file must contain a 'quran_data' list or a list of verses.")

        count = ingester.ingest_quran(quran_data=raw_data)
        return {
            "status": "success",
            "message": f"Successfully ingested {len(raw_data)} verse(s) from '{file.filename}'.",
            "total_verses_in_db": count,
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON file: {str(e)}",
        )


@app.delete("/ingest", tags=["Quran Ingestion"])
def clear_ingestion_endpoint():
    try:
        existing_ids = ingester.collection.get()["ids"]
        if existing_ids:
            ingester.collection.delete(ids=existing_ids)

        return {
            "status": "success",
            "message": "All ingested Quran data has been cleared from ChromaDB.",
            "total_verses_in_db": ingester.collection.count(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear database collection: {str(e)}",
        )


@app.post("/ingest/hadith/file", tags=["Hadith Ingestion"])
async def ingest_hadith_file_endpoint(
    file: UploadFile = File(..., description="Upload a Hadith JSON dataset file (e.g., sahih_bukhari.json)"),
):
    try:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))

        if isinstance(data, dict) and "hadiths" in data:
            raw_data = data["hadiths"]
        elif isinstance(data, list):
            raw_data = data
        else:
            raise ValueError("JSON file must contain a 'hadiths' list or a list of hadith entries.")

        count = hadith_ingester.ingest_hadiths(hadith_data=raw_data)
        return {
            "status": "success",
            "message": f"Successfully ingested {len(raw_data)} hadith(s) from '{file.filename}'.",
            "total_hadiths_in_db": count,
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON file: {str(e)}",
        )

@app.delete("/ingest/hadith", tags=["Hadith Ingestion"])
def clear_hadith_endpoint():
    try:
        existing_ids = hadith_ingester.collection.get()["ids"]
        if existing_ids:
            hadith_ingester.collection.delete(ids=existing_ids)

        return {
            "status": "success",
            "message": "All ingested Hadith data has been cleared from ChromaDB.",
            "total_hadiths_in_db": hadith_ingester.collection.count(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear hadith collection: {str(e)}",
        )


@app.post("/query", tags=["Search & RAG"])
def query_and_chat_endpoint(request: QueryRequest):
    surah_request = detect_full_surah_request(request.query)
    
    if surah_request and request.source_type in ["quran", "both"]:
        surah_num, mode = surah_request
        translations, transliterations, arabics = fetch_entire_surah(surah_num)

        if translations:
            return {
                "query": request.query,
                "retrieved_translations": translations,
                "retrieved_transliterations": transliterations,
                "retrieved_arabic": arabics,
                "retrieved_hadiths": [],
                "chatbot_response": f"Directly retrieved all {len(translations)} verses for Surah {surah_num} from dataset files.",
            }

    quran_docs = []
    hadith_results_data = []

    # Query Quran vector collection
    if request.source_type in ["quran", "both"] and ingester.collection.count() > 0:
        search_results = ingester.query_quran(
            query=request.query,
            n_results=request.n_results,
            surah_filter=request.surah_filter,
        )
        if search_results and search_results.get("documents"):
            quran_docs = search_results["documents"][0]

    # Query Hadith vector collection
    if request.source_type in ["hadith", "both"] and hadith_ingester.collection.count() > 0:
        h_results = hadith_ingester.collection.query(
            query_texts=[request.query],
            n_results=request.n_results,
        )
        if h_results and h_results.get("documents") and h_results.get("metadatas"):
            for doc, meta in zip(h_results["documents"][0], h_results["metadatas"][0]):
                hadith_text = doc.split("| Text: ")[1] if "| Text: " in doc else doc
                hadith_results_data.append({
                    "collection": meta.get("collection", "Hadith"),
                    "hadith_number": meta.get("hadith_number"),
                    "text": hadith_text
                })

    # Combine context for ChatBot LLM prompt
    all_context_docs = quran_docs + [
        f"Source: {h['collection']} (Hadith {h['hadith_number']}) | Text: {h['text']}" 
        for h in hadith_results_data
    ]

    if all_context_docs:
        context_str = "\n".join(all_context_docs)
        augmented_prompt = (
            f"Relevant Scripture and Tradition Context:\n{context_str}\n\n"
            f"Question: {request.query}"
        )
        bot_response = chatbot.ask(augmented_prompt)
    else:
        bot_response = chatbot.ask(request.query)

    # Format structured Quran references
    retrieved_translations = []
    retrieved_transliterations = []
    retrieved_arabic = []

    for doc in quran_docs:
        parsed = parse_surah_verse(doc)
        if parsed:
            surah, verse = parsed
            clean_text = extract_clean_translation(doc)
            retrieved_translations.append({"surah": surah, "verse": verse, "translation": clean_text})
            retrieved_transliterations.append({"surah": surah, "verse": verse, "transliteration": TRANSLITERATION_MAP.get((surah, verse), "Transliteration not found")})
            retrieved_arabic.append({"surah": surah, "verse": verse, "text_arabic": ARABIC_MAP.get((surah, verse), "Arabic text not found")})

    return {
        "query": request.query,
        "retrieved_translations": retrieved_translations,
        "retrieved_transliterations": retrieved_transliterations,
        "retrieved_arabic": retrieved_arabic,
        "retrieved_hadiths": hadith_results_data,
        "chatbot_response": bot_response,
    }


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "active",
        "total_verses_ingested": ingester.collection.count(),
        "total_hadiths_ingested": hadith_ingester.collection.count(),
    }