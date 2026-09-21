import asyncio
from contextlib import asynccontextmanager
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple

from chatbot import ChatBot
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from hadithingester import HadithIngester
from pydantic import BaseModel, Field, field_validator
from quraningester import QuranIngester
from surahlist import SURAH_NAMES

# uvicorn main:app --reload --port 8000 - for server
# python -m http.server 3000 - for client in powershel after going to the ui folder

# --- In-Memory Hash Maps ---
TRANSLITERATION_MAPS: Dict[str, Dict[Tuple[int, int], str]] = {
    "english": {},
    "bangla": {},
    "bosnian": {},
    "chinese": {},
    "french": {},
    "japanese":{},
    "indonesian": {},
    "persian": {}, 
    "spanish": {},
    "malay": {},
    "turkish": {},
    "urdu": {},
    "russian": {}
}
ARABIC_MAP: Dict[Tuple[int, int], str] = {}

TRANSLATION_MAPS: Dict[str, Dict[Tuple[int, int], str]] = {
    "english": {},
    "bangla": {},
    "bosnian": {},
    "chinese": {},
    "french": {},
    "japanese": {},
    "indonesian": {},
    "persian": {},       
    "malay": {},
    "spanish": {},
    "turkish": {},
    "urdu": {},
    "russian": {},
}

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data"


def load_json_dataset(
    file_paths: List[str], target_map: Dict[Tuple[int, int], str], label: str
):
    file_found = False
    for path in file_paths:
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                items = data.get(
                    "quran_data", data if isinstance(data, list) else []
                )
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
        print(
            f"Warning: None of {file_paths} were found. {label.capitalize()}"
            " lookups will return default notices."
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan handler replacing deprecated on_event startup logic."""
    load_json_dataset(
        [
            str(DATA_DIR / "transliteration.json"),
            str(DATA_DIR / "quran_transliteration.json"),
        ],
        TRANSLITERATION_MAPS["english"],
        "English transliteration",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "arabic.json"),
            str(DATA_DIR / "quran_arabic.json"),
        ],
        ARABIC_MAP,
        "Arabic",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "translation.json"),
            str(DATA_DIR / "quran_translation.json"),
            str(DATA_DIR / "quran.json"),
        ],
        TRANSLATION_MAPS["english"],
        "English translation",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "bangla_translation.json"),
        ],
        TRANSLATION_MAPS["bangla"],
        "Bangla translation",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "farsi_translation.json"),
            str(DATA_DIR / "quran_farsi_translation.json"),
            str(DATA_DIR / "khorramdel_farsi_translation.json"),
        ],
        TRANSLATION_MAPS["persian"],
        "Farsi translation",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "bangla_transliteration.json"),
        ],
        TRANSLITERATION_MAPS["bangla"],
        "Bangla transliteration",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "urdu_translation.json"),
        ],
        TRANSLATION_MAPS["urdu"],
        "Urdu translation",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "transliteration.json"),
            str(DATA_DIR / "quran_transliteration.json"),
        ],
        TRANSLITERATION_MAPS["indonesian"],
        "Indonesian transliteration",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "indonesian_translation.json"),
        ],
        TRANSLATION_MAPS["indonesian"],
        "Indonesian translation",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "transliteration.json"),
            str(DATA_DIR / "quran_transliteration.json"),
        ],
        TRANSLITERATION_MAPS["malay"],
        "Malaysian transliteration",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "malay_translation.json"),
        ],
        TRANSLATION_MAPS["malay"],
        "Malaysian translation",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "transliteration.json"),
            str(DATA_DIR / "quran_transliteration.json"),
        ],
        TRANSLITERATION_MAPS["french"],
        "French transliteration",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "french_translation.json"),
        ],
        TRANSLATION_MAPS["french"],
        "French translation",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "transliteration.json"),
            str(DATA_DIR / "quran_transliteration.json"),
        ],
        TRANSLITERATION_MAPS["spanish"],
        "Spanish transliteration",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "spanish_translation.json"),
        ],
        TRANSLATION_MAPS["spanish"],
        "Spanish translation",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "transliteration.json"),
            str(DATA_DIR / "quran_transliteration.json"),
        ],
        TRANSLITERATION_MAPS["turkish"],
        "Turkish transliteration",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "turkish_translation.json"),
        ],
        TRANSLATION_MAPS["turkish"],
        "Turkish translation",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "transliteration.json"),
            str(DATA_DIR / "quran_transliteration.json"),
        ],
        TRANSLITERATION_MAPS["bosnian"],
        "Bosnian transliteration",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "bosnian_translation.json"),
        ],
        TRANSLATION_MAPS["bosnian"],
        "Bosnian translation",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "transliteration.json"),
            str(DATA_DIR / "quran_transliteration.json"),
        ],
        TRANSLITERATION_MAPS["russian"],
        "Russian transliteration",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "russian_translation.json"),
        ],
        TRANSLATION_MAPS["russian"],
        "Russian translation",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "transliteration.json"),
            str(DATA_DIR / "quran_transliteration.json"),
        ],
        TRANSLITERATION_MAPS["chinese"],
        "Chinese transliteration",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "chinese_translation.json"),
        ],
        TRANSLATION_MAPS["chinese"],
        "Chinese translation",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "transliteration.json"),
            str(DATA_DIR / "quran_transliteration.json"),
        ],
        TRANSLITERATION_MAPS["japanese"],
        "Japanese transliteration",
    )
    load_json_dataset(
        [
            str(DATA_DIR / "japanese_translation.json"),
        ],
        TRANSLATION_MAPS["japanese"],
        "Japanese translation",
    )
    yield


# Initialize FastAPI App with modern Lifespan
app = FastAPI(
    title="Quran & Hadith Search & RAG ChatBot API",
    description=(
        "API for ingesting, clearing, and querying Quranic verses and Sahih"
        " Hadiths with LangGraph ChatBot responses."
    ),
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize persistent singletons
ingester = QuranIngester()
hadith_ingester = HadithIngester()
chatbot = ChatBot()


def fetch_entire_surah(
    surah_num: int,
    translation_map: Optional[Dict[Tuple[int, int], str]] = None,
    transliteration_map: Optional[Dict[Tuple[int, int], str]] = None,
) -> Tuple[List[dict], List[dict], List[dict]]:
    """Extracts all verses for a given Surah across translation, transliteration, and Arabic maps."""
    if translation_map is None:
        translation_map = TRANSLATION_MAPS["english"]
    if transliteration_map is None:
        transliteration_map = TRANSLITERATION_MAPS["english"]

    translations, transliterations, arabics = [], [], []
    verse_num = 1

    while True:
        key = (surah_num, verse_num)

        in_trans = key in translation_map
        in_lit = key in transliteration_map
        in_arabic = key in ARABIC_MAP

        if not (in_trans or in_lit or in_arabic):
            break

        translations.append(
            {
                "surah": surah_num,
                "verse": verse_num,
                "translation": translation_map.get(
                    key, "Translation not available"
                ),
            }
        )

        transliterations.append(
            {
                "surah": surah_num,
                "verse": verse_num,
                "transliteration": transliteration_map.get(
                    key, "Transliteration not available"
                ),
            }
        )

        arabics.append(
            {
                "surah": surah_num,
                "verse": verse_num,
                "text_arabic": ARABIC_MAP.get(key, "Arabic text not available"),
            }
        )

        verse_num += 1

    return translations, transliterations, arabics


def detect_full_surah_request(query: str) -> Optional[Tuple[int, str]]:
    cleaned_query = query.lower().strip()

    requested_mode = "translation"
    if "transliteration" in cleaned_query:
        requested_mode = "transliteration"
    elif "arabic" in cleaned_query:
        requested_mode = "arabic"
    elif (
        "translation" in cleaned_query
        or "translate" in cleaned_query
        or "english" in cleaned_query
    ):
        requested_mode = "translation"

    surah_digit_match = re.search(
        r"(?:surah|chapter|soorah)\s+(\d{1,3})", cleaned_query
    )
    if surah_digit_match:
        surah_num = int(surah_digit_match.group(1))
        if 1 <= surah_num <= 114:
            return surah_num, requested_mode

    for name, number in SURAH_NAMES.items():
        pattern = r"\b" + re.escape(name) + r"\b"
        if re.search(pattern, cleaned_query):
            if any(
                k in cleaned_query
                for k in [
                    "give",
                    "show",
                    "get",
                    "read",
                    "translation",
                    "transliteration",
                    "arabic",
                    "text",
                    "surah",
                    "chapter",
                ]
            ):
                return number, requested_mode

    return None


def resolve_surah_num(val: Any) -> Optional[int]:
    """Safely converts string names, numeric strings, or integers to a Surah number (1-114)."""
    if isinstance(val, int):
        return val if 1 <= val <= 114 else None

    cleaned = str(val).strip().lower()

    if cleaned.isdigit():
        num = int(cleaned)
        return num if 1 <= num <= 114 else None

    return SURAH_NAMES.get(cleaned)


def parse_surah_verse(text: str) -> Optional[Tuple[int, int]]:
    match = re.search(r"Surah\s+(\d+),\s*Verse\s+(\d+)", text, re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None


def extract_clean_translation(text: str) -> str:
    if ":" in text:
        return text.split(":", 1)[1].strip()
    return text.strip()


# --- Pydantic Models ---


class QueryRequest(BaseModel):
    query: str = Field(
        ..., examples=["What does the Quran say about patience?"]
    )
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
        default="both",
        description="Target corpus: 'quran', 'hadith', or 'both'",
    )


class SurahRequest(BaseModel):
    surah_num: Any = Field(
        ...,
        description=(
            "Surah identifier - accepts an integer (1-114), a string number"
            " ('18'), or a Surah name ('al-kahf')."
        ),
    )
    language: Optional[str] = Field(
        default="all",
        description=(
            "Language filter (e.g., 'english', 'arabic', 'transliteration',"
            " 'bangla', 'persian', 'urdu', 'all')."
        ),
    )

    @field_validator("surah_num", mode="before")
    @classmethod
    def validate_surah_num(cls, val: Any) -> Any:
        resolved = resolve_surah_num(val)
        if resolved is None:
            raise ValueError(
                f"Invalid Surah identifier: '{val}'. Must be a number (1-114) or valid name."
            )
        return resolved


class VerseItem(BaseModel):
    chapter: int = Field(..., examples=[1])
    verse: int = Field(..., examples=[1])
    text: str = Field(
        ...,
        examples=[
            "In the name of Allah, the Entirely Merciful, the Especially"
            " Merciful."
        ],
    )


class CustomIngestRequest(BaseModel):
    quran_data: Optional[List[VerseItem]] = Field(
        default=None,
        description=(
            "Optional list of custom verse objects to ingest. Omit to trigger"
            " automated download."
        ),
    )


class TranslationRequest(BaseModel):
    text: str
    language: str
    language_name: Optional[str] = None


class TranslationResponse(BaseModel):
    original_text: str
    target_language: str
    translated_text: str


class VerseTranslationRequest(BaseModel):
    chapter: int
    verse: int
    language: str


# --- API Endpoints ---


@app.post("/translate-verse")
async def translate_verse(request: VerseTranslationRequest):
    try:
        key = (request.chapter, request.verse)
        target_lang = request.language.lower().strip()

        # Step 1: Attempt to fetch from loaded JSON in-memory maps
        target_map = TRANSLATION_MAPS.get(target_lang, {})
        translated_text = target_map.get(key)

        # Step 2: Fallback to base English translation or dynamically generate translation via ChatBot
        if not translated_text:
            base_english = TRANSLATION_MAPS["english"].get(
                key, f"Chapter {request.chapter}, Verse {request.verse}"
            )
            prompt = (
                f"Translate the following Quranic verse (Surah {request.chapter}, Verse {request.verse}) "
                f"into {target_lang}. Return ONLY the translation text without commentary:\n\n{base_english}"
            )
            translated_text = await asyncio.to_thread(chatbot.ask, prompt)
            translated_text = translated_text.strip()

        return {
            "chapter": request.chapter,
            "verse": request.verse,
            "language": target_lang,
            "translated_text": translated_text,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transliterate-verse")
async def transliterate_verse(request: VerseTranslationRequest):
    try:
        key = (request.chapter, request.verse)
        target_lang = request.language.lower().strip()

        # Step 1: Attempt to fetch from loaded JSON in-memory transliteration maps
        target_map = TRANSLITERATION_MAPS.get(target_lang, {})
        transliterated_text = target_map.get(key)

        # Step 2: Fallback to base English transliteration or dynamically generate via ChatBot
        if not transliterated_text:
            base_english = TRANSLITERATION_MAPS.get("english", {}).get(
                key, f"Chapter {request.chapter}, Verse {request.verse}"
            )
            prompt = (
                f"Provide the phonetic transliteration of the following Quranic verse (Surah {request.chapter}, Verse {request.verse}) "
                f"optimized for readers using {target_lang} script/phonetics. Return ONLY the transliteration text without commentary:\n\n{base_english}"
            )
            transliterated_text = await asyncio.to_thread(chatbot.ask, prompt)
            transliterated_text = transliterated_text.strip()

        return {
            "chapter": request.chapter,
            "verse": request.verse,
            "language": target_lang,
            "transliterated_text": transliterated_text,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/surah", tags=["Search Surah Directly"])
def surah_endpoint(request: SurahRequest):
    surah_num = request.surah_num

    requested_language = (request.language or "english").lower().strip()

    target_translation_map = TRANSLATION_MAPS.get(
        requested_language, TRANSLATION_MAPS["english"]
    )
    target_transliteration_map = TRANSLITERATION_MAPS.get(
        requested_language, TRANSLITERATION_MAPS["english"]
    )

    translations, transliterations, arabics = fetch_entire_surah(
        surah_num,
        translation_map=target_translation_map,
        transliteration_map=target_transliteration_map,
    )

    if not translations and not arabics and not transliterations:
        return {
            "surah_num": surah_num,
            "language": request.language,
            "message": f"No verses found for Surah {surah_num}.",
            "retrieved_translations": [],
            "retrieved_transliterations": [],
            "retrieved_arabic": [],
            "chatbot_response": f"No verses found for Surah {surah_num}.",
        }

    return {
        "surah_num": surah_num,
        "language": request.language,
        "retrieved_translations": translations,
        "retrieved_transliterations": transliterations,
        "retrieved_arabic": arabics,
        "chatbot_response": "",
    }


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
            "message": (
                f"Successfully ingested {len(raw_data)} verse(s) into ChromaDB."
            ),
            "total_verses_in_db": count,
        }
    else:
        background_tasks.add_task(ingester.ingest_quran)
        return {
            "status": "processing",
            "message": "Full Quran ingestion task started in the background.",
        }


@app.post("/ingest/hadith", tags=["Hadith Ingestion"])
def ingest_hadith_endpoint(
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    background_tasks.add_task(hadith_ingester.ingest_hadiths)
    return {
        "status": "processing",
        "message": (
            "Sahih al-Bukhari and Sahih Muslim background ingestion task"
            " started."
        ),
    }


@app.post("/ingest/file", tags=["Quran Ingestion"])
async def ingest_quran_file_endpoint(
    file: UploadFile = File(
        ..., description="Upload a JSON dataset file (e.g., quran_dataset.json)"
    ),
):
    try:
        content = await file.read()
        data = await asyncio.to_thread(json.loads, content.decode("utf-8"))

        if isinstance(data, dict) and "quran_data" in data:
            raw_data = data["quran_data"]
        elif isinstance(data, list):
            raw_data = data
        else:
            raise ValueError(
                "JSON file must contain a 'quran_data' list or a list of"
                " verses."
            )

        count = await asyncio.to_thread(ingester.ingest_quran, quran_data=raw_data)
        return {
            "status": "success",
            "message": (
                f"Successfully ingested {len(raw_data)} verse(s) from"
                f" '{file.filename}'."
            ),
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
    file: UploadFile = File(
        ...,
        description=(
            "Upload a Hadith JSON dataset file (e.g., sahih_bukhari.json)"
        ),
    ),
):
    try:
        content = await file.read()
        data = await asyncio.to_thread(json.loads, content.decode("utf-8"))

        if isinstance(data, dict) and "hadiths" in data:
            raw_data = data["hadiths"]
        elif isinstance(data, list):
            raw_data = data
        else:
            raise ValueError(
                "JSON file must contain a 'hadiths' list or a list of hadith"
                " entries."
            )

        count = await asyncio.to_thread(
            hadith_ingester.ingest_hadiths, hadith_data=raw_data
        )
        return {
            "status": "success",
            "message": (
                f"Successfully ingested {len(raw_data)} hadith(s) from"
                f" '{file.filename}'."
            ),
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


@app.post("/translate", response_model=TranslationResponse)
async def translate_text(payload: TranslationRequest):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    source_language = payload.language_name or payload.language

    if not source_language or not source_language.strip():
        raise HTTPException(
            status_code=400, detail="Source language must be provided."
        )

    prompt = (
        f"Translate the following text from {source_language} into English. "
        "Provide only the English translation without any explanation,"
        f" context, or conversational fluff:\n\n{payload.text}"
    )

    try:
        translated_text = await asyncio.to_thread(chatbot.ask, prompt)
        return TranslationResponse(
            original_text=payload.text,
            target_language="English",
            translated_text=translated_text.strip(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Translation failed: {str(e)}"
        )


@app.post("/translate-from-english", response_model=TranslationResponse)
async def translate_from_english(payload: TranslationRequest):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    target_language = payload.language_name or payload.language

    if not target_language or not target_language.strip():
        raise HTTPException(
            status_code=400, detail="Target language must be provided."
        )

    prompt = (
        f"Translate the following English text into {target_language}. Provide"
        f" only the {target_language} translation without any explanation,"
        f" context, or conversational fluff:\n\n{payload.text}"
    )

    try:
        translated_text = await asyncio.to_thread(chatbot.ask, prompt)
        return TranslationResponse(
            original_text=payload.text,
            target_language=target_language,
            translated_text=translated_text.strip(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Translation failed: {str(e)}"
        )


@app.post("/query", tags=["Search & RAG"])
def query_and_chat_endpoint(request: QueryRequest):
    surah_request = detect_full_surah_request(request.query)

    if surah_request and request.source_type in ["quran", "both"]:
        surah_num, mode = surah_request
        translations, transliterations, arabics = fetch_entire_surah(
            surah_num,
            translation_map=TRANSLATION_MAPS["english"],
            transliteration_map=TRANSLITERATION_MAPS["english"],
        )

        if translations:
            return {
                "query": request.query,
                "retrieved_translations": translations,
                "retrieved_transliterations": transliterations,
                "retrieved_arabic": arabics,
                "retrieved_hadiths": [],
                "chatbot_response": (
                    f"Directly retrieved all {len(translations)} verses for"
                    f" Surah {surah_num} from dataset files."
                ),
            }

    quran_docs = []
    hadith_results_data = []

    if request.source_type in ["quran", "both"] and ingester.collection.count() > 0:
        search_results = ingester.query_quran(
            query=request.query,
            n_results=request.n_results,
            surah_filter=request.surah_filter,
        )
        if search_results and search_results.get("documents"):
            quran_docs = search_results["documents"][0]

    if (
        request.source_type in ["hadith", "both"]
        and hadith_ingester.collection.count() > 0
    ):
        h_results = hadith_ingester.collection.query(
            query_texts=[request.query],
            n_results=request.n_results,
        )
        if (
            h_results
            and h_results.get("documents")
            and h_results.get("metadatas")
        ):
            for doc, meta in zip(
                h_results["documents"][0], h_results["metadatas"][0]
            ):
                hadith_text = (
                    doc.split("| Text: ")[1] if "| Text: " in doc else doc
                )
                hadith_results_data.append(
                    {
                        "collection": meta.get("collection", "Hadith"),
                        "hadith_number": meta.get("hadith_number"),
                        "text": hadith_text,
                    }
                )

    all_context_docs = quran_docs + [
        f"Source: {h['collection']} (Hadith {h['hadith_number']}) | Text:"
        f" {h['text']}"
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

    retrieved_translations = []
    retrieved_transliterations = []
    retrieved_arabic = []

    # Default to English transliterations for vector search results
    default_lit_map = TRANSLITERATION_MAPS["english"]

    for doc in quran_docs:
        parsed = parse_surah_verse(doc)
        if parsed:
            surah, verse = parsed
            clean_text = extract_clean_translation(doc)
            retrieved_translations.append(
                {"surah": surah, "verse": verse, "translation": clean_text}
            )
            retrieved_transliterations.append(
                {
                    "surah": surah,
                    "verse": verse,
                    "transliteration": default_lit_map.get(
                        (surah, verse), "Transliteration not found"
                    ),
                }
            )
            retrieved_arabic.append(
                {
                    "surah": surah,
                    "verse": verse,
                    "text_arabic": ARABIC_MAP.get(
                        (surah, verse), "Arabic text not found"
                    ),
                }
            )

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