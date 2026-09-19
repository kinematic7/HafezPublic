// App.js
import { LANGUAGES } from "./libs/languages.js";

import { 
  SURAHS,
  SURAHS_BANGLA

} from "./libs/surahs.js";

import {
  PLACEHOLDER_TEXTS,
  TRANSLATION_NOTES,
  APP_TITLES,
  QURAN_HADITH_LABELS,
  QURAN_ONLY_LABELS,
  HADITH_ONLY_LABELS,
  ARABIC_LABELS,
  SURAH_LABELS,
  LANGUAGE_LABELS,
  WELCOME_LABELS,
  VERSE_RANGE_PAGE_FILTER_LABELS,
  SHOWING_LABELS,
  SEARCHING_DATABASE_LABELS,
  FROM_LABELS,
  TO_LABELS,
  OF_LABELS,
  AYAH_LABELS,
  RETRIEVED_QURANIC_REFERENCES_LABELS,
  ASSISTANT_LABELS,
  YOU_LABELS,
  RETRIEVED_SAHIH_HADITH_REFERENCES_LABELS,
  TRANSLATION_LABELS,
  TRANSLITERATION_LABELS,
} from "./libs/translations.js";

const { useState, useEffect, useLayoutEffect, useRef, useMemo, useCallback } = React;

const SURAH_VERSE_COUNTS = {
  1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75, 9: 129, 10: 109,
  11: 123, 12: 111, 13: 43, 14: 52, 15: 99, 16: 128, 17: 111, 18: 110, 19: 98, 20: 135,
  21: 112, 22: 78, 23: 118, 24: 64, 25: 77, 26: 227, 27: 93, 28: 88, 29: 69, 30: 60,
  31: 34, 32: 30, 33: 73, 34: 54, 35: 45, 36: 83, 37: 182, 38: 88, 39: 75, 40: 85,
  41: 54, 42: 53, 43: 89, 44: 59, 45: 37, 46: 35, 47: 38, 48: 29, 49: 18, 50: 45,
  51: 60, 52: 49, 53: 62, 54: 55, 55: 78, 56: 96, 57: 29, 58: 22, 59: 24, 60: 13,
  61: 14, 62: 11, 63: 11, 64: 18, 65: 12, 66: 12, 67: 30, 68: 52, 69: 52, 70: 44,
  71: 28, 72: 28, 73: 20, 74: 56, 75: 40, 76: 31, 77: 50, 78: 40, 79: 46, 80: 42,
  81: 29, 82: 19, 83: 36, 84: 25, 85: 22, 86: 17, 87: 19, 88: 26, 89: 30, 90: 20,
  91: 15, 92: 21, 93: 11, 94: 8, 95: 8, 96: 19, 97: 5, 98: 8, 99: 8, 100: 11,
  101: 11, 102: 8, 103: 3, 104: 9, 105: 5, 106: 4, 107: 7, 108: 3, 109: 6, 110: 3,
  111: 5, 112: 4, 113: 5, 114: 6
};

// Standalone Helper: Translate content from English via Backend API
async function translateFromEnglish(sourceText, languageCode, selectedLangObj) {
  if (
    !languageCode ||
    languageCode.toLowerCase() === "english" ||
    languageCode.toLowerCase() === "en" ||
    languageCode.toLowerCase() === "arabic" ||
    languageCode.toLowerCase() === "ar"
  ) {
    return sourceText;
  }

  const targetLanguageName = selectedLangObj?.name || languageCode;

  try {
    const response = await fetch("http://localhost:8000/translate-from-english", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        text: sourceText,
        language_name: targetLanguageName,
        language: languageCode
      })
    });

    if (!response.ok) {
      throw new Error(`Translation request failed: ${response.statusText}`);
    }

    const data = await response.json();
    return data.translated_text || sourceText;
  } catch (err) {
    console.error("translateFromEnglish error:", err);
    return sourceText;
  }
}

function renderFormattedText(text) {
  if (!text) return null;
  const lines = text.split("\n");

  return lines.map((line, lineIdx) => {
    const parts = line.split(/(\*\*.*?\*\*)/g);

    return (
      <React.Fragment key={lineIdx}>
        {parts.map((part, i) => {
          if (part.startsWith("**") && part.endsWith("**")) {
            return (
              <strong key={i} className="strong-highlight">
                {part.slice(2, -2)}
              </strong>
            );
          }
          return part;
        })}
        {lineIdx < lines.length - 1 && <br />}
      </React.Fragment>
    );
  });
}

function TranslatedVerse({ text, language, selectedLangObj, disableTranslation }) {
  const [displayText, setDisplayText] = useState(text);
  const [translating, setTranslating] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const isEnglish =
      !language ||
      language.toLowerCase() === "english" ||
      language.toLowerCase() === "en";

    const isArabic =
      language.toLowerCase() === "arabic" ||
      language.toLowerCase() === "ar";

    if (disableTranslation || isEnglish || isArabic) {
      setDisplayText(text);
      return;
    }

    const performTranslation = async () => {
      setTranslating(true);
      try {
        const result = await translateFromEnglish(text, language, selectedLangObj);
        if (isMounted) {
          setDisplayText(result || text);
        }
      } catch (err) {
        console.error("Verse translation failed:", err);
        if (isMounted) setDisplayText(text);
      } finally {
        if (isMounted) setTranslating(false);
      }
    };

    performTranslation();

    return () => {
      isMounted = false;
    };
  }, [text, language, selectedLangObj, disableTranslation]);

  if (translating) {
    return <span style={{ opacity: 0.6, fontStyle: "italic" }}>Translating verse...</span>;
  }

  return renderFormattedText(displayText);
}

function TranslatedHadith({ text, language, selectedLangObj, disableTranslation }) {
  const [displayText, setDisplayText] = useState(text);
  const [translating, setTranslating] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const isEnglish =
      !language ||
      language.toLowerCase() === "english" ||
      language.toLowerCase() === "en";

    if (disableTranslation || isEnglish) {
      setDisplayText(text);
      return;
    }

    const performTranslation = async () => {
      setTranslating(true);
      try {
        const result = await translateFromEnglish(text, language, selectedLangObj);
        if (isMounted) {
          setDisplayText(result || text);
        }
      } catch (err) {
        console.error("Hadith translation failed:", err);
        if (isMounted) setDisplayText(text);
      } finally {
        if (isMounted) setTranslating(false);
      }
    };

    performTranslation();

    return () => {
      isMounted = false;
    };
  }, [text, language, selectedLangObj, disableTranslation]);

  if (translating) {
    return <span style={{ opacity: 0.6, fontStyle: "italic" }}>Translating hadith...</span>;
  }

  return renderFormattedText(displayText);
}

function QuranSearchApp() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const [theme, setTheme] = useState("dark");
  const [sourceType, setSourceType] = useState("both"); // 'both' | 'quran' | 'hadith'
  const [language, setLanguage] = useState("english");
  const activeSurahs = (language === "bangla" || language === "bn") ? SURAHS_BANGLA : SURAHS;

  const [selectedSurah, setSelectedSurah] = useState("all");

  const [showArabic, setShowArabic] = useState(true);
  const [showTransliteration, setShowTransliteration] = useState(true);
  const [showTranslation, setShowTranslation] = useState(true);

  const [fromVerse, setFromVerse] = useState(1);
  const [toVerse, setToVerse] = useState(1);

  const lastUserMessageRef = useRef(null);

  // Requirement 1: Clear chat on language change
  useEffect(() => {
    setMessages([]);
  }, [language]);

  useEffect(() => {
    const linkElement = document.getElementById("theme-stylesheet");
    if (linkElement) {
      linkElement.href = theme === "dark" ? "dark.css" : "light.css";
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  useEffect(() => {
    if (loading && lastUserMessageRef.current) {
      lastUserMessageRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [loading]);

  const activeVerseContext = useMemo(() => {
    const lastMsg = messages[messages.length - 1];
    if (!lastMsg || lastMsg.role !== "assistant" || !lastMsg.verses?.length) {
      return null;
    }
    const firstSurah = lastMsg.verses[0].surah;
    const allSameSurah = lastMsg.verses.every((v) => v.surah === firstSurah);
    const maxPossible =
      allSameSurah && SURAH_VERSE_COUNTS[firstSurah]
        ? SURAH_VERSE_COUNTS[firstSurah]
        : lastMsg.verses.length;

    return {
      totalCount: lastMsg.verses.length,
      maxPossible,
      surah: firstSurah,
      isFullSurah: allSameSurah && lastMsg.verses.length === maxPossible
    };
  }, [messages]);

  useLayoutEffect(() => {
    if (activeVerseContext) {
      setFromVerse(1);
      setToVerse(activeVerseContext.totalCount);
    }
  }, [activeVerseContext]);

  const selectedLangObj = useMemo(() => {
    const found = LANGUAGES.find(
      (l) => l.code === language || l.name?.toLowerCase() === language.toLowerCase()
    );
    return found || { code: language, name: language };
  }, [language]);

  const translateContent = useCallback(async (sourceText, langObj, langCode) => {
    if (!langCode || langCode.toLowerCase() === "english") {
      return sourceText;
    }

    const targetLanguageName = langObj?.name || langCode;

    const response = await fetch("http://localhost:8000/translate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        text: sourceText,
        language_name: targetLanguageName,
        language: langCode
      })
    });

    if (!response.ok) {
      throw new Error(`Translation failed: ${response.statusText}`);
    }

    const data = await response.json();
    return data.translated_text || sourceText;
  }, []);

  const handleSend = async (overrideQuery = null) => {
    let queryToSend = overrideQuery || query;
    if (!queryToSend.trim() || loading) return;

    let currentQuery = queryToSend.trim();
    if (!(currentQuery.startsWith("[") && currentQuery.endsWith("]"))) {
      currentQuery = currentQuery.replace(/surah/gi, "surâh");
    }

    setQuery("");
    setLoading(true);

    setMessages([{ role: "user", content: currentQuery, isStructured: false }]);

    let languageInstruction = "";
    if (language === "english") {
      languageInstruction = "\n\n(Respond in English)";
    } else {
      const selectedLangLabel = selectedLangObj ? selectedLangObj.name : language;
      currentQuery = await translateContent(currentQuery, selectedLangObj, language);
      languageInstruction = `\n\n(Respond strictly in ${selectedLangLabel}. Please translate the response, as well as the full relevant Quranic verses and Hadith sources, completely into ${selectedLangLabel}. Quote the entire quranic verse or hadith.)`;
    }

    const finalPayloadQuery = currentQuery + languageInstruction;

    try {
      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: {
          accept: "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          query: finalPayloadQuery,
          n_results: 5,
          surah_filter: 0,
          source_type: sourceType,
          language: language
        })
      });

      if (!response.ok) {
        throw new Error("Server returned status " + response.status);
      }

      const data = await response.json();
      const note = TRANSLATION_NOTES[language] || "";
      if (data.chatbot_response) {
        data.chatbot_response += `\n\n${note}`;
      }

      if (
        typeof data === "object" &&
        data !== null &&
        (data.chatbot_response ||
          data.retrieved_arabic ||
          data.retrieved_translations ||
          data.retrieved_hadiths)
      ) {
        const transliterationMap = new Map(
          (data.retrieved_transliterations || []).map((item) => [
            `${item.surah}:${item.verse}`,
            item.transliteration
          ])
        );

        const arabicMap = new Map(
          (data.retrieved_arabic || []).map((item) => [
            `${item.surah}:${item.verse}`,
            item.text_arabic
          ])
        );

        const verses = (data.retrieved_translations || []).map((translationObj) => {
          const key = `${translationObj.surah}:${translationObj.verse}`;
          return {
            surah: translationObj.surah,
            verse: translationObj.verse,
            translation: translationObj.translation || "",
            arabic: arabicMap.get(key) || "",
            transliteration: transliterationMap.get(key) || ""
          };
        });

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            isStructured: true,
            isSurahView: false,
            summary: data.chatbot_response || "",
            verses: verses,
            hadiths: data.retrieved_hadiths || []
          }
        ]);
      } else {
        const textFallback =
          typeof data === "string"
            ? data
            : data.response || data.answer || JSON.stringify(data, null, 2);

        setMessages((prev) => [
          ...prev,
          { role: "assistant", isStructured: false, content: textFallback }
        ]);
      }
    } catch (err) {
      console.error("Fetch error:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          isStructured: false,
          content: "Error contacting server on port 8000."
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

 const handleSurahSelect = async (e) => {
    const value = e.target.value;
    if (value === "all" || loading) return;

    const surahObj = SURAHS.find((s) => String(s.id) === value);
    if (!surahObj) return;

    const selectedSurahNum = Number(surahObj.id);

    setQuery("");
    setLoading(true);

    const userPromptText = `[Surah ${selectedSurahNum}: ${surahObj.name_en}]`;
    
    // CHANGE 1: Overwrite messages array completely instead of using prev state
    setMessages([{ role: "user", content: userPromptText, isStructured: false }]);

    try {
      const response = await fetch("http://localhost:8000/surah", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          surah_num: selectedSurahNum,
          language: language,
        }),
      });

      if (!response.ok) {
        throw new Error(`Surah request failed with status ${response.status}`);
      }

      const data = await response.json();

      // 1. Build Arabic Map with String Key Normalization and Key Fallbacks
      const arabicMap = new Map();
      (data.retrieved_arabic || []).forEach((item) => {
        const key = `${String(item.surah)}:${String(item.verse)}`;
        const arabicText = item.text_arabic || item.text || item.arabic || "";
        arabicMap.set(key, arabicText);
      });

      // 2. Build Transliteration Map with String Key Normalization and Key Fallbacks
      const transliterationMap = new Map();
      (data.retrieved_transliterations || []).forEach((item) => {
        const key = `${String(item.surah)}:${String(item.verse)}`;
        const transliterationText = item.transliteration || item.transliteration_text || item.text || "";
        transliterationMap.set(key, transliterationText);
      });

      // 3. Map into unified Verse structures
      const verses = (data.retrieved_translations || []).map((translationObj) => {
        const key = `${String(translationObj.surah)}:${String(translationObj.verse)}`;

        return {
          surah: translationObj.surah,
          verse: translationObj.verse,
          translation: translationObj.translation || translationObj.text || translationObj.translation_text || "",
          arabic: arabicMap.get(key) || translationObj.text_arabic || translationObj.arabic || "",
          transliteration: transliterationMap.get(key) || translationObj.transliteration || "",
        };
      });

      const note = TRANSLATION_NOTES[language] || "";
 
      const surahName = (language === "bangla" || language === "bn")
        ? (SURAHS_BANGLA[surahObj?.id]?.name_bn || SURAHS_BANGLA.find?.(s => s.id === surahObj?.id)?.name_bn || surahObj?.name_en)
        : surahObj?.name_en;

      const summaryText = data?.chatbot_response
        ? `${data.chatbot_response}\n\n${note}`
        : `${SURAH_LABELS[language] || SURAH_LABELS.english || "Surah"} ${(language === "bangla" || language === "bn") ? (SURAHS_BANGLA[surahObj?.id - 1]?.name_bn || SURAHS_BANGLA.find?.(s => s.id === surahObj?.id)?.name_bn || surahObj?.name_en) : surahObj?.name_en} (${surahObj?.name_ar}) `;
            

      // CHANGE 2: Replace state with exact 2-item array (User Prompt + Assistant Response)
      setMessages([
        { role: "user", content: userPromptText, isStructured: false },
        {
          role: "assistant",
          isStructured: true,
          isSurahView: true,
          summary: summaryText,
          verses: verses,
          hadiths: data.retrieved_hadiths || [],
        },
      ]);
    } catch (error) {
      console.error("Error fetching Surah:", error);
      
      // CHANGE 3: Overwrite state with error response replacing old messages
      setMessages([
        { role: "user", content: userPromptText, isStructured: false },
        {
          role: "assistant",
          isStructured: false,
          content: `Error fetching Surah ${selectedSurahNum} from server on port 8000.`,
        },
      ]);
    } finally {
      setLoading(false);
      setSelectedSurah("all");
    }
  };
  
  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  const lastUserMsgIndex = messages.reduce((lastIdx, msg, idx) => {
    return msg.role === "user" ? idx : lastIdx;
  }, -1);

  const isArabicSelected =
    language.toLowerCase() === "arabic" || language.toLowerCase() === "ar";

  return (
    <div className="app-container">
      {/* CORPUS FILTER BAR */}
      <div
        style={{
          background: "rgba(16, 185, 129, 0.15)",
          borderBottom: "1px solid rgba(16, 185, 129, 0.3)",
          padding: "10px 20px",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: "15px",
          flexWrap: "wrap"
        }}
      >
        <span
          className="hide-on-mobile"
          style={{ fontSize: "12px", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.5px" }}
        >
          <span className="title-icon">﷽</span> {APP_TITLES[language] || "Quran & Hadith Insights"}:
        </span>
        <div style={{ display: "flex", background: "rgba(0,0,0,0.3)", padding: "4px", borderRadius: "8px", gap: "6px" }}>
          {["both", "quran", "hadith"].map((type) => {
            const labels = {
              both: QURAN_HADITH_LABELS[language] || "Quran & Hadith",
              quran: QURAN_ONLY_LABELS[language] || "Quran Only",
              hadith: HADITH_ONLY_LABELS[language] || "Hadith Only"
            };
            return (
              <button
                key={type}
                onClick={() => setSourceType(type)}
                style={{
                  padding: "6px 14px",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontWeight: "600",
                  fontSize: "12px",
                  background: sourceType === type ? "#059669" : "transparent",
                  color: sourceType === type ? "#fff" : "inherit",
                  transition: "all 0.2s"
                }}
              >
                {labels[type]}
              </button>
            );
          })}
        </div>
      </div>

      {/* HEADER */}
<div className="app-header">
  <div className="header-actions" style={{ display: "flex", alignItems: "center", gap: "15px", flexWrap: "wrap" }}>
          {/* LANGUAGE DROPDOWN */}
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span className="hide-on-mobile" style={{ fontSize: "12px", fontWeight: "600" }}>
              {LANGUAGE_LABELS[language] || "Language"}:
            </span>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              aria-label="Select Language"
              style={{
                padding: "6px 10px",
                borderRadius: "6px",
                border: "1px solid rgba(16, 185, 129, 0.4)",
                background: "rgba(0, 0, 0, 0.2)",
                color: "inherit",
                fontSize: "12px",
                fontWeight: "600",
                cursor: "pointer"
              }}
            >
              {LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code} style={{ background: "#1f2937", color: "#fff" }}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>

          {/* SURAH DROPDOWN */}
          {(
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span className="hide-on-mobile" style={{ fontSize: "12px", fontWeight: "600" }}>
                {SURAH_LABELS[language] || "Surah"}:
              </span>
             <select
                value={selectedSurah}
                onChange={handleSurahSelect}
                disabled={loading}
                aria-label="Select Surah"
                style={{
                  padding: "6px 10px",
                  borderRadius: "6px",
                  border: "1px solid rgba(16, 185, 129, 0.4)",
                  background: "rgba(0, 0, 0, 0.2)",
                  color: "inherit",
                  fontSize: "12px",
                  fontWeight: "600",
                  cursor: "pointer"
                }}
              >
                <option value="all" style={{ background: "#1f2937", color: "#fff" }}>
                  {language === "bangla" || language === "bn" ? "সকল সূরা" : "All Surahs"}
                </option>
                {activeSurahs.map((surah) => (
                  <option key={surah.id} value={surah.id} style={{ background: "#1f2937", color: "#fff" }}>
                    {surah.id}. {surah.name_bn || surah.name_en} ({surah.name_ar})
                  </option>
                ))}
              </select>
            </div>
          )}       

          {/* DISPLAY CONTROLS */}
          {(!isArabicSelected &&  
          <div className="display-controls hide-on-mobile">
            <label className="switch-control">
              <input
                type="checkbox"
                checked={showArabic}
                onChange={(e) => setShowArabic(e.target.checked)}
              />
              <span>{ARABIC_LABELS[language] || "Arabic"}</span>
            </label>
            <label className="switch-control">
                  <input
                    type="checkbox"
                    checked={showTranslation}
                    onChange={(e) => setShowTranslation(e.target.checked)}
                  />
                  <span>{TRANSLATION_LABELS[language] || "Translation"}</span>
            </label>

            {(
              <>
                <label className="switch-control">
                  <input
                    type="checkbox"
                    checked={showTransliteration}
                    onChange={(e) => setShowTransliteration(e.target.checked)}
                  />
                  <span>{TRANSLITERATION_LABELS[language] || "Transliteration"}</span>
                </label>

               
              </>
            )}
          </div>
        )}

          {/* THEME SWITCH WRAPPER */}
          <div className="theme-switch-wrapper">
            <span className="theme-icon">☀️</span>
            <label className="theme-switch">
              <input
                type="checkbox"
                checked={theme === "dark"}
                onChange={toggleTheme}
                aria-label="Toggle dark/light mode"
              />
              <span className="theme-slider"></span>
            </label>
            <span className="theme-icon">🌙</span>
          </div>
        </div>
      </div>

      {/* VERSE / PAGE FILTER BAR */}
      {activeVerseContext && activeVerseContext.totalCount > 1 && (
        <div className="surah-range-filter-bar hide-on-mobile">
          <div className="range-title-group">
            <span className="range-icon">⚙</span>
            <span className="range-title">
              {VERSE_RANGE_PAGE_FILTER_LABELS[language] || "Verse Range / Page Filter"}
            </span>
          </div>

          <div className="range-inputs">
            <label>
              {FROM_LABELS[language] || "From"}:
              <input
                type="number"
                min="1"
                max={toVerse}
                value={fromVerse}
                onChange={(e) => setFromVerse(Math.max(1, Number(e.target.value)))}
              />
            </label>

            <label>
              {TO_LABELS[language] || "To"}:
              <input
                type="number"
                min={fromVerse}
                max={activeVerseContext.totalCount}
                value={toVerse}
                onChange={(e) =>
                  setToVerse(Math.min(activeVerseContext.totalCount, Number(e.target.value)))
                }
              />
            </label>
            <span className="range-count-badge">
              {SHOWING_LABELS[language] || "Showing"}{" "}
              {Math.min(toVerse - fromVerse + 1, activeVerseContext.totalCount)}{" "}
              {OF_LABELS[language] || "of"} {activeVerseContext.totalCount}
            </span>
          </div>
        </div>
      )}

      {/* CHAT WINDOW */}
      <div className="chat-window">
        {messages.length === 0 && (
          <div className="empty-state-card">
            <img
              src="./islam.png"
              alt="Islamic Symbol"
              style={{ width: "200px", height: "200px", objectFit: "contain" }}
            />
            <h3
              style={{
                fontFamily: "serif",
                fontSize: "1.6rem",
                color: "var(--primary)",
                marginBottom: "0.75rem",
                lineHeight: "1.8"
              }}
            >
              بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ
            </h3>
            <p style={{ fontSize: "0.9rem", fontWeight: "normal" }}>
              {WELCOME_LABELS[language] ||
                "Welcome! Ask about Quranic verses, Hadiths, or Islamic themes to get started."}
            </p>
          </div>
        )}

        {messages.map((msg, idx) => {
          const isLatestAssistantMessage =
            idx === messages.length - 1 && msg.role === "assistant";

          const visibleVerses =
            isLatestAssistantMessage && activeVerseContext && activeVerseContext.totalCount > 1
              ? (msg.verses || []).filter((_, index) => {
                  const itemNum = index + 1;
                  return itemNum >= fromVerse && itemNum <= toVerse;
                })
              : msg.verses || [];

          return (
            <div
              key={idx}
              ref={idx === lastUserMsgIndex ? lastUserMessageRef : null}
              className={`message-bubble ${
                msg.role === "user" ? "message-user" : "message-assistant"
              }`}
            >
              <div className="message-header-row">
                <span
                  className={`message-role-label ${
                    msg.role === "user" ? "role-user" : "role-assistant"
                  }`}
                >
                  {msg.role === "user"
                    ? YOU_LABELS[language] || "You"
                    : ASSISTANT_LABELS[language] || "Assistant"}
                </span>
              </div>

              {!msg.isStructured && (
                <div className="user-text">{renderFormattedText(msg.content)}</div>
              )}

              {msg.isStructured && (
                <div>
                  {msg.summary && (
                    <div className="summary-box">{renderFormattedText(msg.summary)}</div>
                  )}

                  {/* Quran References Section */}
                  {visibleVerses.length > 0 && (
                    <div>
                      <div className="verses-section-header">
                        <span>
                          {RETRIEVED_QURANIC_REFERENCES_LABELS[language] ||
                            "Retrieved Quranic References"}
                        </span>
                      </div>

                      {visibleVerses.map((verse, vIdx) => (
                        <div key={vIdx} className="verse-card">
                          <div className="verse-badge-container">
                            <span className="verse-badge">
                              {SURAH_LABELS[language] || "Surah"} {verse.surah} •{" "}
                              {AYAH_LABELS[language] || "Ayah"} {verse.verse}
                            </span>
                          </div>

                          {showArabic && verse.arabic && (
                            <div className="arabic-text">{verse.arabic}</div>
                          )}

                          {!isArabicSelected && showTransliteration && verse.transliteration && verse.transliteration!="Transliteration not available" && (
                            <div className="transliteration-text">
                              {verse.transliteration}
                            </div>
                          )}

                          {/* Skip translation rendering if Arabic is selected */}
                          {!isArabicSelected && showTranslation && verse.translation && (
                            <div className="verse-translation-text">
                              <TranslatedVerse
                                key={`${verse.surah}-${verse.verse}-${language}`}
                                text={verse.translation}
                                language={language}
                                selectedLangObj={selectedLangObj}
                                disableTranslation={msg.isSurahView}
                              />
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Hadith References Section */}
                  {msg.hadiths && msg.hadiths.length > 0 && (
                    <div style={{ marginTop: "20px" }}>
                      <div className="verses-section-header">
                        <span>{RETRIEVED_SAHIH_HADITH_REFERENCES_LABELS[language] || "Retrieved Sahih Hadith References"}</span>
                      </div>

                      {msg.hadiths.map((hadith, hIdx) => (
                        <div
                          key={hIdx}
                          className="verse-card"
                          style={{ borderLeft: "4px solid #10b981" }}
                        >
                          <div className="verse-badge-container">
                            <span className="verse-badge" style={{ background: "#065f46" }}>
                              <span>{hadith.collection} •  #{hadith.hadith_number}</span>
                            </span>
                          </div>

                          <div className="english-translation" style={{ marginTop: "8px" }}>
                            <TranslatedHadith
                              key={`hadith-${hIdx}-${language}`}
                              text={hadith.text}
                              language={language}
                              selectedLangObj={selectedLangObj}
                              disableTranslation={msg.isSurahView}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}

        {loading && (
          <div className="loading-box">
            <div className="spinner"></div>
            <span>{SEARCHING_DATABASE_LABELS[language] || "Searching..."}</span>
          </div>
        )}
      </div>

      {/* INPUT BAR */}
      <div className="input-container">
        <input
          className="chat-input"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            PLACEHOLDER_TEXTS[language] || "Ask about verses, hadiths, or themes..."
          }
          disabled={loading}
        />

        <button
          className="send-button"
          onClick={() => handleSend()}
          disabled={loading || !query.trim()}
        >
          {loading ? "..." : "➤"}
        </button>
      </div>
    </div>
  );
}

const container = document.getElementById("root");
const root = ReactDOM.createRoot(container);
root.render(<QuranSearchApp />);