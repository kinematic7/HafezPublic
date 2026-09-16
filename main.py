import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple

from chatbot import ChatBot
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from hadithingester import HadithIngester
from pydantic import BaseModel, Field
from quraningester import QuranIngester

# Initialize FastAPI App
app = FastAPI(
    title="Quran & Hadith Search & RAG ChatBot API",
    description=(
        "API for ingesting, clearing, and querying Quranic verses and Sahih"
        " Hadiths with LangGraph ChatBot responses."
    ),
    version="1.1.0",
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

# --- In-Memory Hash Maps ---
TRANSLITERATION_MAP: Dict[Tuple[int, int], str] = {}
ARABIC_MAP: Dict[Tuple[int, int], str] = {}
TRANSLATION_MAP: Dict[Tuple[int, int], str] = {}

# Surah Names mapping (1-114) for fuzzy query parsing
SURAH_NAMES: dict[str, int] = {
    # 1. Al-Fatihah
    "fatiha": 1,
    "al-fatiha": 1,
    "alfatiha": 1,
    "al-fatihah": 1,
    "fatihah": 1,
    "opening": 1,
    # 2. Al-Baqarah
    "baqarah": 2,
    "al-baqarah": 2,
    "albaqarah": 2,
    "cow": 2,
    # 3. Ali 'Imran
    "imran": 3,
    "ali 'imran": 3,
    "ali imran": 3,
    "al-imran": 3,
    "alimran": 3,
    # 4. An-Nisa
    "an-nisa": 4,
    "nisa": 4,
    "annisa": 4,
    "women": 4,
    # 5. Al-Ma'idah
    "al-maidah": 5,
    "maidah": 5,
    "al-ma'idah": 5,
    "table": 5,
    # 6. Al-An'am
    "al-an'am": 6,
    "al-anam": 6,
    "anam": 6,
    "cattle": 6,
    # 7. Al-A'raf
    "al-a'raf": 7,
    "al-araf": 7,
    "araf": 7,
    # 8. Al-Anfal
    "al-anfal": 8,
    "anfal": 8,
    # 9. At-Tawbah
    "at-tawbah": 9,
    "tawbah": 9,
    "repentance": 9,
    # 10. Yunus
    "yunus": 10,
    "yunas": 10,
    # 11. Hud
    "hud": 11,
    # 12. Yusuf
    "yusuf": 12,
    "joseph": 12,
    # 13. Ar-Ra'd
    "ar-ra'd": 13,
    "ar-rad": 13,
    "rad": 13,
    "thunder": 13,
    # 14. Ibrahim
    "ibrahim": 14,
    "abraham": 14,
    # 15. Al-Hijr
    "al-hijr": 15,
    "hijr": 15,
    # 16. An-Nahl
    "an-nahl": 16,
    "nahl": 16,
    "bee": 16,
    # 17. Al-Isra
    "al-isra": 17,
    "isra": 17,
    # 18. Al-Kahf
    "kahf": 18,
    "al-kahf": 18,
    "cave": 18,
    # 19. Maryam
    "maryam": 19,
    "mary": 19,
    # 20. Taha
    "taha": 20,
    "ta-ha": 20,
    # 21. Al-Anbiya
    "al-anbiya": 21,
    "anbiya": 21,
    "prophets": 21,
    # 22. Al-Hajj
    "al-hajj": 22,
    "hajj": 22,
    "pilgrimage": 22,
    # 23. Al-Mu'minun
    "al-mu'minun": 23,
    "al-muminun": 23,
    "muminun": 23,
    # 24. An-Nur
    "an-nur": 24,
    "nur": 24,
    "light": 24,
    # 25. Al-Furqan
    "al-furqan": 25,
    "furqan": 25,
    # 26. Ash-Shu'ara
    "ash-shu'ara": 26,
    "ash-shuara": 26,
    "shuara": 26,
    "poets": 26,
    # 27. An-Naml
    "an-naml": 27,
    "naml": 27,
    "ant": 27,
    # 28. Al-Qasas
    "al-qasas": 28,
    "qasas": 28,
    # 29. Al-'Ankabut
    "al-'ankabut": 29,
    "al-ankabut": 29,
    "ankabut": 29,
    "spider": 29,
    # 30. Ar-Rum
    "ar-rum": 30,
    "rum": 30,
    "romans": 30,
    # 31. Luqman
    "luqman": 31,
    # 32. As-Sajdah
    "as-sajdah": 32,
    "sajdah": 32,
    "prostration": 32,
    # 33. Al-Ahzab
    "al-ahzab": 33,
    "ahzab": 33,
    # 34. Saba
    "saba": 34,
    "sheba": 34,
    # 35. Fatir
    "fatir": 35,
    # 36. Ya-Sin
    "yasin": 36,
    "ya-sin": 36,
    "yaseen": 36,
    # 37. As-Saffat
    "as-saffat": 37,
    "saffat": 37,
    # 38. Sad
    "sad": 38,
    # 39. Az-Zumar
    "az-zumar": 39,
    "zumar": 39,
    # 40. Ghafir
    "ghafir": 40,
    "mumin": 40,
    # 41. Fussilat
    "fussilat": 41,
    # 42. Ash-Shura
    "ash-shura": 42,
    "shura": 42,
    # 43. Az-Zukhruf
    "az-zukhruf": 43,
    "zukhruf": 43,
    # 44. Ad-Dukhan
    "ad-dukhan": 44,
    "dukhan": 44,
    "smoke": 44,
    # 45. Al-Jathiyah
    "al-jathiyah": 45,
    "jathiyah": 45,
    # 46. Al-Ahqaf
    "al-ahqaf": 46,
    "ahqaf": 46,
    # 47. Muhammad
    "muhammad": 47,
    # 48. Al-Fath
    "al-fath": 48,
    "fath": 48,
    "victory": 48,
    # 49. Al-Hujurat
    "al-hujurat": 49,
    "hujurat": 49,
    # 50. Qaf
    "qaf": 50,
    # 51. Adh-Dhariyat
    "adh-dhariyat": 51,
    "dhariyat": 51,
    # 52. At-Tur
    "at-tur": 52,
    "tur": 52,
    # 53. An-Najm
    "an-najm": 53,
    "najm": 53,
    "star": 53,
    # 54. Al-Qamar
    "al-qamar": 54,
    "qamar": 54,
    "moon": 54,
    # 55. Ar-Rahman
    "ar-rahman": 55,
    "rahman": 55,
    # 56. Al-Waqi'ah
    "al-waqi'ah": 56,
    "al-waqiah": 56,
    "waqiah": 56,
    # 57. Al-Hadid
    "al-hadid": 57,
    "hadid": 57,
    "iron": 57,
    # 58. Al-Mujadila
    "al-mujadila": 58,
    "mujadila": 58,
    # 59. Al-Hashr
    "al-hashr": 59,
    "hashr": 59,
    # 60. Al-Mumtahanah
    "al-mumtahanah": 60,
    "mumtahanah": 60,
    # 61. As-Saff
    "as-saff": 61,
    "saff": 61,
    # 62. Al-Jumu'ah
    "al-jumu'ah": 62,
    "al-jumuah": 62,
    "jumuah": 62,
    "friday": 62,
    # 63. Al-Munafiqun
    "al-munafiqun": 63,
    "munafiqun": 63,
    # 64. At-Taghabun
    "at-taghabun": 64,
    "taghabun": 64,
    # 65. At-Talaq
    "at-talaq": 65,
    "talaq": 65,
    "divorce": 65,
    # 66. At-Tahrim
    "at-tahrim": 66,
    "tahrim": 66,
    # 67. Al-Mulk
    "al-mulk": 67,
    "mulk": 67,
    "sovereignty": 67,
    # 68. Al-Qalam
    "al-qalam": 68,
    "qalam": 68,
    "pen": 68,
    # 69. Al-Haqqah
    "al-haqqah": 69,
    "haqqah": 69,
    # 70. Al-Ma'arij
    "al-ma'arij": 70,
    "al-maarij": 70,
    "maarij": 70,
    # 71. Nuh
    "nuh": 71,
    "noah": 71,
    # 72. Al-Jinn
    "al-jinn": 72,
    "jinn": 72,
    # 73. Al-Muzzammil
    "al-muzzammil": 73,
    "muzzammil": 73,
    # 74. Al-Muddaththir
    "al-muddaththir": 74,
    "muddaththir": 74,
    # 75. Al-Qiyamah
    "al-qiyamah": 75,
    "qiyamah": 75,
    "resurrection": 75,
    # 76. Al-Insan
    "al-insan": 76,
    "insan": 76,
    # 77. Al-Mursalat
    "al-mursalat": 77,
    "mursalat": 77,
    # 78. An-Naba
    "an-naba": 78,
    "naba": 78,
    # 79. An-Nazi'at
    "an-nazi'at": 79,
    "an-naziat": 79,
    "naziat": 79,
    # 80. 'Abasa
    "'abasa": 80,
    "abasa": 80,
    # 81. At-Takwir
    "at-takwir": 81,
    "takwir": 81,
    # 82. Al-Infitar
    "al-infitar": 82,
    "infitar": 82,
    # 83. Al-Mutaffifin
    "al-mutaffifin": 83,
    "mutaffifin": 83,
    # 84. Al-Inshiqaq
    "al-inshiqaq": 84,
    "inshiqaq": 84,
    # 85. Al-Buruj
    "al-buruj": 85,
    "buruj": 85,
    # 86. At-Tariq
    "at-tariq": 86,
    "tariq": 86,
    # 87. Al-A'la
    "al-a'la": 87,
    "al-ala": 87,
    "ala": 87,
    # 88. Al-Ghashiyah
    "al-ghashiyah": 88,
    "ghashiyah": 88,
    # 89. Al-Fajr
    "al-fajr": 89,
    "fajr": 89,
    "dawn": 89,
    # 90. Al-Balad
    "al-balad": 90,
    "balad": 90,
    "city": 90,
    # 91. Ash-Shams
    "ash-shams": 91,
    "shams": 91,
    "sun": 91,
    # 92. Al-Layl
    "al-layl": 92,
    "layl": 92,
    "night": 92,
    # 93. Ad-Duha
    "ad-duha": 93,
    "duha": 93,
    # 94. Ash-Sharh
    "ash-sharh": 94,
    "sharh": 94,
    "inshirah": 94,
    # 95. At-Tin
    "at-tin": 95,
    "tin": 95,
    "fig": 95,
    # 96. Al-'Alaq
    "al-'alaq": 96,
    "al-alaq": 96,
    "alaq": 96,
    # 97. Al-Qadr
    "al-qadr": 97,
    "qadr": 97,
    # 98. Al-Bayyinah
    "al-bayyinah": 98,
    "bayyinah": 98,
    # 99. Az-Zalzalah
    "az-zalzalah": 99,
    "zalzalah": 99,
    "zilzal": 99,
    # 100. Al-'Adiyat
    "al-'adiyat": 100,
    "al-adiyat": 100,
    "adiyat": 100,
    # 101. Al-Qari'ah
    "al-qari'ah": 101,
    "al-qariah": 101,
    "qariah": 101,
    # 102. At-Takathur
    "at-takathur": 102,
    "takathur": 102,
    # 103. Al-'Asr
    "al-'asr": 103,
    "al-asr": 103,
    "asr": 103,
    # 104. Al-Humazah
    "al-humazah": 104,
    "humazah": 104,
    # 105. Al-Fil
    "al-fil": 105,
    "fil": 105,
    "elephant": 105,
    # 106. Quraysh
    "quraysh": 106,
    # 107. Al-Ma'un
    "al-ma'un": 107,
    "al-maun": 107,
    "maun": 107,
    # 108. Al-Kawthar
    "al-kawthar": 108,
    "kawthar": 108,
    "kauthar": 108,
    # 109. Al-Kafirun
    "al-kafirun": 109,
    "kafirun": 109,
    # 110. An-Nasr
    "an-nasr": 110,
    "nasr": 110,
    # 111. Al-Masad
    "al-masad": 111,
    "masad": 111,
    "lahab": 111,
    # 112. Al-Ikhlas
    "al-ikhlas": 112,
    "ikhlas": 112,
    # 113. Al-Falaq
    "al-falaq": 113,
    "falaq": 113,
    # 114. An-Nas
    "an-nas": 114,
    "nas": 114,
}


def load_json_dataset(
    file_paths: List[str], target_map: Dict[Tuple[int, int], str], label: str
):
    """Helper to load dataset JSON files into a (chapter, verse) hash map."""
    file_found = False
    for path in file_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
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


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data"


@app.on_event("startup")
def load_datasets():
    """Loads translation, transliteration, and Arabic JSON datasets into O(1) hash maps on app startup."""
    load_json_dataset(
        [
            str(DATA_DIR / "transliteration.json"),
            str(DATA_DIR / "quran_transliteration.json"),
        ],
        TRANSLITERATION_MAP,
        "transliteration",
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
        TRANSLATION_MAP,
        "translation",
    )


def fetch_entire_surah(
    surah_num: int,
) -> Tuple[List[dict], List[dict], List[dict]]:
    """Extracts all verses for a given Surah across translation, transliteration, and Arabic maps."""
    translations, transliterations, arabics = [], [], []
    verse_num = 1

    while True:
        key = (surah_num, verse_num)

        in_trans = key in TRANSLATION_MAP
        in_lit = key in TRANSLITERATION_MAP
        in_arabic = key in ARABIC_MAP

        if not (in_trans or in_lit or in_arabic):
            break

        translations.append({
            "surah": surah_num,
            "verse": verse_num,
            "translation": TRANSLATION_MAP.get(
                key, "Translation not available"
            ),
        })

        transliterations.append({
            "surah": surah_num,
            "verse": verse_num,
            "transliteration": TRANSLITERATION_MAP.get(
                key, "Transliteration not available"
            ),
        })

        arabics.append({
            "surah": surah_num,
            "verse": verse_num,
            "text_arabic": ARABIC_MAP.get(key, "Arabic text not available"),
        })

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
            " 'all')."
        ),
    )


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


# --- API Endpoints ---


@app.post("/surah", tags=["Search Surah Directly"])
def surah_endpoint(request: SurahRequest):
    surah_num = resolve_surah_num(request.surah_num)

    if not surah_num:
        return {
            "error": f"Invalid Surah identifier: '{request.surah_num}'. Please provide a valid Surah name or number between 1 and 114."
        }

    translations, transliterations, arabics = fetch_entire_surah(surah_num)

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
        "chatbot_response": f"Directly retrieved Surah {surah_num}.",
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
        data = json.loads(content.decode("utf-8"))

        if isinstance(data, dict) and "quran_data" in data:
            raw_data = data["quran_data"]
        elif isinstance(data, list):
            raw_data = data
        else:
            raise ValueError(
                "JSON file must contain a 'quran_data' list or a list of"
                " verses."
            )

        count = ingester.ingest_quran(quran_data=raw_data)
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
        data = json.loads(content.decode("utf-8"))

        if isinstance(data, dict) and "hadiths" in data:
            raw_data = data["hadiths"]
        elif isinstance(data, list):
            raw_data = data
        else:
            raise ValueError(
                "JSON file must contain a 'hadiths' list or a list of hadith"
                " entries."
            )

        count = hadith_ingester.ingest_hadiths(hadith_data=raw_data)
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
        translated_text = chatbot.ask(prompt)
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
        translated_text = chatbot.ask(prompt)
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
        translations, transliterations, arabics = fetch_entire_surah(surah_num)

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
                hadith_results_data.append({
                    "collection": meta.get("collection", "Hadith"),
                    "hadith_number": meta.get("hadith_number"),
                    "text": hadith_text,
                })

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

    for doc in quran_docs:
        parsed = parse_surah_verse(doc)
        if parsed:
            surah, verse = parsed
            clean_text = extract_clean_translation(doc)
            retrieved_translations.append(
                {"surah": surah, "verse": verse, "translation": clean_text}
            )
            retrieved_transliterations.append({
                "surah": surah,
                "verse": verse,
                "transliteration": TRANSLITERATION_MAP.get(
                    (surah, verse), "Transliteration not found"
                ),
            })
            retrieved_arabic.append({
                "surah": surah,
                "verse": verse,
                "text_arabic": ARABIC_MAP.get(
                    (surah, verse), "Arabic text not found"
                ),
            })

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