const { useState, useEffect, useRef, useMemo } = React;

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

function QuranSearchApp() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const [theme, setTheme] = useState("dark");
  const [sourceType, setSourceType] = useState("both"); // 'both' | 'quran' | 'hadith'

  const [showArabic, setShowArabic] = useState(true);
  const [showTransliteration, setShowTransliteration] = useState(true);
  const [showTranslation, setShowTranslation] = useState(true);

  const [fromVerse, setFromVerse] = useState(1);
  const [toVerse, setToVerse] = useState(1);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    const linkElement = document.getElementById("theme-stylesheet");
    if (linkElement) {
      linkElement.href = theme === "dark" ? "dark.css" : "light.css";
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const activeVerseContext = useMemo(() => {
    const lastMsg = messages[messages.length - 1];
    if (!lastMsg || lastMsg.role !== "assistant" || !lastMsg.verses?.length) {
      return null;
    }
    const firstSurah = lastMsg.verses[0].surah;
    const allSameSurah = lastMsg.verses.every((v) => v.surah === firstSurah);
    const maxPossible = allSameSurah && SURAH_VERSE_COUNTS[firstSurah] ? SURAH_VERSE_COUNTS[firstSurah] : lastMsg.verses.length;

    return {
      totalCount: lastMsg.verses.length,
      maxPossible,
      surah: firstSurah,
      isFullSurah: allSameSurah && lastMsg.verses.length === maxPossible
    };
  }, [messages]);

  useEffect(() => {
    if (activeVerseContext) {
      setFromVerse(1);
      setToVerse(activeVerseContext.totalCount);
    }
  }, [activeVerseContext]);

  const handleSend = async () => {
    if (!query.trim() || loading) return;

    const currentQuery = query;
    setQuery("");
    setLoading(true);

    setMessages((prev) => [
      ...prev,
      { role: "user", content: currentQuery, isStructured: false }
    ]);

    try {
      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: {
          accept: "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          query: currentQuery,
          n_results: 5,
          surah_filter: 0,
          source_type: sourceType
        })
      });

      if (!response.ok) {
        throw new Error("Server returned status " + response.status);
      }

      const data = await response.json();

      if (
        typeof data === "object" &&
        data !== null &&
        (data.chatbot_response || data.retrieved_arabic || data.retrieved_translations || data.retrieved_hadiths)
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

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  return (
    <div className="app-container">
      {/* STANDALONE CORPUS FILTER BAR AT THE VERY TOP */}
      <div style={{ background: "rgba(16, 185, 129, 0.15)", borderBottom: "1px solid rgba(16, 185, 129, 0.3)", padding: "10px 20px", display: "flex", justifyContent: "center", alignItems: "center", gap: "15px", flexWrap: "wrap" }}>
        <span style={{ fontSize: "12px", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.5px" }}>Search Corpus Filter:</span>
        <div style={{ display: "flex", background: "rgba(0,0,0,0.3)", padding: "4px", borderRadius: "8px", gap: "6px" }}>
          <button
            onClick={() => setSourceType("both")}
            style={{
              padding: "6px 14px",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              fontWeight: "600",
              fontSize: "12px",
              background: sourceType === "both" ? "#059669" : "transparent",
              color: sourceType === "both" ? "#fff" : "inherit",
              transition: "all 0.2s"
            }}
          >
            Quran + Hadith
          </button>
          <button
            onClick={() => setSourceType("quran")}
            style={{
              padding: "6px 14px",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              fontWeight: "600",
              fontSize: "12px",
              background: sourceType === "quran" ? "#059669" : "transparent",
              color: sourceType === "quran" ? "#fff" : "inherit",
              transition: "all 0.2s"
            }}
          >
            Quran Only
          </button>
          <button
            onClick={() => setSourceType("hadith")}
            style={{
              padding: "6px 14px",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              fontWeight: "600",
              fontSize: "12px",
              background: sourceType === "hadith" ? "#059669" : "transparent",
              color: sourceType === "hadith" ? "#fff" : "inherit",
              transition: "all 0.2s"
            }}
          >
            Hadith Only
          </button>
        </div>
      </div>

      {/* HEADER */}
      <div className="app-header">
        <div className="app-title-area">
          <h2 className="app-title">
            <span className="title-icon">﷽</span> Quran & Hadith Insights
          </h2>
          <span className="app-subtitle">Hafez - Dual-Corpus AI Search</span>
        </div>

        <div className="header-actions" style={{ display: "flex", alignItems: "center", gap: "15px", flexWrap: "wrap" }}>
          <div className="display-controls">
            <label className="switch-control">
              <input
                type="checkbox"
                checked={showArabic}
                onChange={(e) => setShowArabic(e.target.checked)}
              />
              <span>Arabic</span>
            </label>

            <label className="switch-control">
              <input
                type="checkbox"
                checked={showTransliteration}
                onChange={(e) => setShowTransliteration(e.target.checked)}
              />
              <span>Transliteration</span>
            </label>

            <label className="switch-control">
              <input
                type="checkbox"
                checked={showTranslation}
                onChange={(e) => setShowTranslation(e.target.checked)}
              />
              <span>English</span>
            </label>
          </div>

          <div className="theme-switch-wrapper">
            <span className="theme-icon">☀️</span>
            <label className="theme-switch">
              <input
                type="checkbox"
                checked={theme === "dark"}
                onChange={toggleTheme}
              />
              <span className="theme-slider"></span>
            </label>
            <span className="theme-icon">🌙</span>
          </div>
        </div>
      </div>

      {/* PERSISTENT VERSE / PAGE FILTER BAR */}
      {activeVerseContext && activeVerseContext.totalCount > 1 && (
        <div className="surah-range-filter-bar">
          <div className="range-title-group">
            <span className="range-icon">⚙</span>
            <span className="range-title">Verse Range / Page Filter</span>
          </div>

          <div className="range-inputs">
            <label>
              From:
              <input
                type="number"
                min="1"
                max={toVerse}
                value={fromVerse}
                onChange={(e) => setFromVerse(Math.max(1, Number(e.target.value)))}
              />
            </label>

            <label>
              To:
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
              Showing {Math.min(toVerse - fromVerse + 1, activeVerseContext.totalCount)} of {activeVerseContext.totalCount}
            </span>

          </div>
        </div>
      )}

      {/* CHAT WINDOW */}
      <div className="chat-window">
        {messages.length === 0 && (
          <div className="empty-state-card">
            <div className="empty-icon">📖</div>
            <h3>Explore Scripture & Tradition</h3>
            <p>Use the top corpus filter banner to query Quranic verses, Sahih Hadiths, or both simultaneously.</p>
          </div>
        )}

        {messages.map((msg, idx) => {
          const isLatestAssistantMessage = idx === messages.length - 1 && msg.role === "assistant";

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
                  {msg.role === "user" ? "You" : "Assistant"}
                </span>
              </div>

              {!msg.isStructured && (
                <div className="user-text">{renderFormattedText(msg.content)}</div>
              )}

              {msg.isStructured && (
                <div>
                  {msg.summary && (
                    <div className="summary-box">
                      {renderFormattedText(msg.summary)}
                    </div>
                  )}

                  {/* Quran References Section */}
                  {visibleVerses.length > 0 && (
                    <div>
                      <div className="verses-section-header">
                        <span>Retrieved Quranic References</span>
                      </div>

                      {visibleVerses.map((verse, vIdx) => (
                        <div key={vIdx} className="verse-card">
                          <div className="verse-badge-container">
                            <span className="verse-badge">
                              Surah {verse.surah} • Ayah {verse.verse}
                            </span>
                          </div>

                          {showArabic && verse.arabic && (
                            <div className="arabic-text">{verse.arabic}</div>
                          )}

                          {showTransliteration && verse.transliteration && (
                            <div className="transliteration-text">
                              {verse.transliteration}
                            </div>
                          )}

                          {showTranslation && verse.translation && (
                            <div className="english-translation">
                              {renderFormattedText(verse.translation)}
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
                        <span>Retrieved Sahih Hadith References</span>
                      </div>

                      {msg.hadiths.map((hadith, hIdx) => (
                        <div key={hIdx} className="verse-card" style={{ borderLeft: "4px solid #10b981" }}>
                          <div className="verse-badge-container">
                            <span className="verse-badge" style={{ background: "#065f46" }}>
                              {hadith.collection} • Hadith #{hadith.hadith_number}
                            </span>
                          </div>

                          <div className="english-translation" style={{ marginTop: "8px" }}>
                            {renderFormattedText(hadith.text)}
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
            <span>Searching database and generating response...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* INPUT BAR */}
      <div className="input-container">
        <input
          className="chat-input"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about verses, hadiths, or themes..."
          disabled={loading}
        />

        <button
          className="send-button"
          onClick={handleSend}
          disabled={loading || !query.trim()}
        >
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}

const container = document.getElementById("root");
const root = ReactDOM.createRoot(container);
root.render(<QuranSearchApp />);