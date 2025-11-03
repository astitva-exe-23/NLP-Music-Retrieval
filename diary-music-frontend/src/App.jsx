import { useEffect, useMemo, useState } from "react";
import { health, getRecommendations } from "./api";

function Visualizer() {
  return (
    <div className="visualizer" aria-hidden="true">
      {Array.from({ length: 12 }).map((_, i) => (
        <div key={i} className="bar" />
      ))}
    </div>
  );
}

const LANG_MAP = {
  english: "en",
  spanish: "es",
  hindi: "hi",
  french: "fr",
  portuguese: "pt",
  italian: "it",
  korean: "ko",
  japanese: "ja",
  german: "de",
  tamil: "ta",
  telugu: "te",
  instrumental: "instrumental",
};

export default function App() {
  const [ready, setReady] = useState(null);
  const [diary, setDiary] = useState("");
  const [language, setLanguage] = useState("");
  const [k, setK] = useState(10);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [data, setData] = useState(null);

  useEffect(() => {
    health().then(r => setReady(r.ready)).catch(() => setReady(false));
  }, []);

  const statusText = useMemo(() => {
    if (ready === null) return "checking…";
    return ready ? "ready" : "not ready";
  }, [ready]);

  const onSubmit = async (e) => {
    e.preventDefault();
    setErr(""); 
    setData(null); 
    setLoading(true);

    const langInput = language.trim().toLowerCase();
    const langCode = LANG_MAP[langInput] || language || null;

    try {
      const payload = {
        diary_text: diary.trim(),
        k,
        filters: langCode ? { language: langCode } : undefined,
      };

      const res = await getRecommendations(payload);
      setData(res);

    } catch (e) {
      setErr(e?.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <div className="logo" />
          <div>
            <div className="title">Daily Diary → Music</div>
            <div className="status">Your feelings? Your Music</div>
          </div>
        </div>
        <Visualizer />
      </header>

      <div className="grid">
        <section className="card">
          <h3>Tell us about your day</h3>

          <form onSubmit={onSubmit} style={{ display: "grid", gap: 12 }}>
            <label className="label">Diary</label>
            <textarea
              className="textarea"
              placeholder="Long day? Excited? What happened…"
              value={diary}
              onChange={(e) => setDiary(e.target.value)}
              required
            />

            <div className="row">
              <div style={{ flex: 1 }}>
                <label className="label">Language (optional)</label>
                <input
                  list="languages"
                  className="input"
                  placeholder="Select or type…"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                />
                <datalist id="languages">
                  <option value="english" />
                  <option value="spanish" />
                  <option value="hindi" />
                  <option value="french" />
                  <option value="portuguese" />
                  <option value="italian" />
                  <option value="korean" />
                  <option value="japanese" />
                  <option value="german" />
                  <option value="tamil" />
                  <option value="telugu" />
                  <option value="instrumental" />
                </datalist>
              </div>

              <div style={{ width: 120 }}>
                <label className="label">Top K</label>
                <input
                  className="input"
                  type="number"
                  min={1}
                  max={50}
                  value={k}
                  onChange={(e) => setK(parseInt(e.target.value || "10", 10))}
                />
              </div>
            </div>

            <button className="button" disabled={loading || !diary.trim()}>
              {loading ? "Finding vibes…" : "Get songs"}
            </button>

            {err && <div className="error">Error: {err}</div>}
          </form>
        </section>

        <section className="card">
          <h3>Query Verification</h3>
          {!data ? (
            <div className="trace-item">Submit to see normalized query and facets.</div>
          ) : (
            <>
              <div className="trace-item"><strong>Normalized Query From LLM:</strong> {data.trace.normalized_query}</div>
          
              {data.trace.facets.topics?.length ? (
                <div className="trace-item">
                  <strong>Topics:</strong> {data.trace.facets.topics.join(", ")}
                </div>
              ) : null}
            </>
          )}
        </section>
      </div>

      <section className="card" style={{ marginTop: 18 }}>
        <h3>Results {data ? `(${data.items.length})` : ""}</h3>

        {!data ? (
          <div className="trace-item">Your recommendations will show up here.</div>
        ) : !data.items.length ? (
          <div className="trace-item">No matches.</div>
        ) : (
          <ul className="list">
            {data.items.map((t, i) => (
              <li key={`${t.id}-${i}`} className="item">
                <div className="track">
                  <div className="meta">

                    {/* ✅ Title + Artist */}
                    <div className="titleline">
                      {t.title?.replace(/\b\w/g, c => c.toUpperCase())} —{" "}
                      {t.artist?.replace(/\b\w/g, c => c.toUpperCase())}
                    </div>

                    {/* ✅ Match label */}
                    <div className="sub">
                      <span className="match">
                        {t.score >= 0.70 ? "Perfect match 🤍" :
                         t.score >= 0.60 ? "Great match 💫" :
                         t.score >= 0.50 ? "Good match 🙂" :
                         t.score >= 0.40 ? "Decent match 👌" :
                         "Vibe explore 🎧"}
                      </span>
                    </div>

                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
