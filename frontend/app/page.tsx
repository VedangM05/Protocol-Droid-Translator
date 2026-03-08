"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Globe,
  Mic,
  FileText,
  ArrowLeftRight,
  Loader2,
  Volume2,
  AlertCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";

const API_BASE = ""; // use relative URL so Next.js rewrites proxy to localhost:8000

const DOMAINS = [
  { id: "General", label: "General" },
  { id: "Healthcare (Medical)", label: "Healthcare" },
  { id: "Legal/Governance", label: "Legal" },
] as const;

export default function Home() {
  const [languages, setLanguages] = useState<string[]>([]);
  const [sourceLang, setSourceLang] = useState("Auto Detect");
  const [targetLang, setTargetLang] = useState("Hindi");
  const [domain, setDomain] = useState("General");
  const [inputText, setInputText] = useState("");
  const [outputText, setOutputText] = useState("");
  const [confidence, setConfidence] = useState<number | null>(null);
  const [detectedLang, setDetectedLang] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ttsUrl, setTtsUrl] = useState<string | null>(null);
  const [inputTab, setInputTab] = useState<"text" | "mic" | "file">("text");

  // Fetch languages on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/languages`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data.languages)) setLanguages(data.languages);
      })
      .catch(() => setLanguages(["English", "Hindi", "Spanish", "French"]));
  }, []);

  const swapLanguages = useCallback(() => {
    if (sourceLang === "Auto Detect") return;
    setSourceLang(targetLang);
    setTargetLang(sourceLang);
    setInputText(outputText);
    setOutputText(inputText);
  }, [sourceLang, targetLang, inputText, outputText]);

  const handleTranslate = useCallback(async () => {
    const text = inputText.trim();
    if (!text) {
      setError("Enter some text to translate.");
      return;
    }
    setError(null);
    setLoading(true);
    setTtsUrl(null);
    try {
      const res = await fetch(`${API_BASE}/api/translate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text,
          source_lang: sourceLang,
          target_lang: targetLang,
          domain,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || res.statusText || "Translation failed");
      }
      const data = await res.json();
      setOutputText(data.text ?? "");
      setConfidence(data.confidence ?? null);
      setDetectedLang(data.detected_lang?.lang_name ?? null);

      // TTS
      if (data.text) {
        try {
          const ttsRes = await fetch(`${API_BASE}/api/tts`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: data.text, target_lang: targetLang }),
          });
          if (ttsRes.ok) {
            const blob = await ttsRes.blob();
            setTtsUrl(URL.createObjectURL(blob));
          }
        } catch {
          // ignore TTS errors
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }, [inputText, sourceLang, targetLang, domain]);

  const sourceOptions = ["Auto Detect", ...languages];
  const targetOptions = languages.length ? languages : ["English", "Hindi"];

  return (
    <main
      className="min-h-screen"
      style={{
        background:
          "radial-gradient(circle at 15% 50%, #1c0936 0%, #080f26 40%, #030514 100%)",
      }}
    >
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Hero */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-3xl md:text-4xl font-bold mb-1 bg-gradient-to-r from-[#00C9FF] to-[#92FE9D] bg-clip-text text-transparent">
            BhashaEngine Pro
          </h1>
          <p className="text-zinc-400 text-sm">Universal Neural Translation • Offline First</p>
        </motion.header>

        {/* Domain pills */}
        <div className="flex flex-wrap justify-center gap-2 mb-6">
          {DOMAINS.map((d) => (
            <button
              key={d.id}
              type="button"
              onClick={() => setDomain(d.id)}
              className={cn(
                "px-4 py-2 rounded-full text-sm font-medium transition-all",
                domain === d.id
                  ? "bg-[#00C9FF]/20 text-[#00C9FF] border border-[#00C9FF]/50"
                  : "bg-white/5 text-zinc-400 border border-white/10 hover:border-white/20 hover:text-zinc-300"
              )}
            >
              {d.label}
            </button>
          ))}
        </div>

        {/* Language row + swap */}
        <div className="flex flex-wrap items-center gap-4 mb-4">
          <div className="flex-1 min-w-[140px]">
            <label className="block text-xs text-zinc-500 mb-1">From</label>
            <select
              value={sourceLang}
              onChange={(e) => setSourceLang(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white focus:border-[#00C9FF]/50 focus:ring-1 focus:ring-[#00C9FF]/30 outline-none"
            >
              {sourceOptions.map((l) => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>
          </div>
          <div className="flex-shrink-0 pt-6">
            <motion.button
              type="button"
              onClick={swapLanguages}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              className="w-12 h-12 rounded-full bg-white/10 border border-white/20 flex items-center justify-center text-white hover:bg-[#00C9FF]/20 hover:border-[#00C9FF]/50"
              title="Swap languages"
            >
              <ArrowLeftRight className="w-5 h-5" />
            </motion.button>
          </div>
          <div className="flex-1 min-w-[140px]">
            <label className="block text-xs text-zinc-500 mb-1">To</label>
            <select
              value={targetLang}
              onChange={(e) => setTargetLang(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white focus:border-[#00C9FF]/50 focus:ring-1 focus:ring-[#00C9FF]/30 outline-none"
            >
              {targetOptions.map((l) => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Input / Output panels */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          {/* Input card */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md p-4"
          >
            <div className="flex gap-2 mb-3">
              {[
                { id: "text" as const, icon: FileText, label: "Text" },
                { id: "mic" as const, icon: Mic, label: "Mic" },
                { id: "file" as const, icon: Globe, label: "File" },
              ].map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setInputTab(tab.id)}
                  className={cn(
                    "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
                    inputTab === tab.id
                      ? "bg-[#00C9FF]/20 text-[#00C9FF]"
                      : "text-zinc-400 hover:text-zinc-300"
                  )}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              ))}
            </div>
            {inputTab === "text" && (
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Type or paste text to translate..."
                className="w-full h-40 px-4 py-3 rounded-xl bg-black/20 border border-white/10 text-white placeholder-zinc-500 focus:border-[#00C9FF]/50 focus:ring-1 focus:ring-[#00C9FF]/30 outline-none resize-none"
                disabled={loading}
              />
            )}
            {inputTab === "mic" && (
              <div className="h-40 flex items-center justify-center text-zinc-500 text-sm rounded-xl bg-black/20 border border-white/10">
                Mic input: upload an audio file in the File tab or use your OS voice input, then paste here.
              </div>
            )}
            {inputTab === "file" && (
              <div className="h-40 flex items-center justify-center text-zinc-500 text-sm rounded-xl bg-black/20 border border-white/10 border-dashed">
                Document upload: use API /api/translate/document or paste extracted text in Text tab.
              </div>
            )}
            {sourceLang === "Auto Detect" && inputText.trim() && (
              <p className="mt-2 text-xs text-zinc-500">
                Detected: {detectedLang ?? "…"}
              </p>
            )}
          </motion.div>

          {/* Output card */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md p-4"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-zinc-500">Translation</span>
              {confidence != null && (
                <span className="text-xs text-[#92FE9D]">
                  {Math.round(confidence)}% confidence
                </span>
              )}
            </div>
            <div className="min-h-[10rem] rounded-xl bg-black/20 border border-white/10 p-4 text-[#00C9FF]/90 whitespace-pre-wrap">
              <AnimatePresence mode="wait">
                {loading && (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex items-center gap-2 text-zinc-400"
                  >
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Translating…
                  </motion.div>
                )}
                {!loading && outputText && (
                  <motion.p
                    key="output"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  >
                    {outputText}
                  </motion.p>
                )}
                {!loading && !outputText && (
                  <motion.p
                    key="placeholder"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-zinc-500 italic"
                  >
                    Translation will appear here…
                  </motion.p>
                )}
              </AnimatePresence>
            </div>
            {ttsUrl && (
              <div className="mt-2">
                <audio src={ttsUrl} controls className="w-full h-9" />
              </div>
            )}
          </motion.div>
        </div>

        {/* Error */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-4 flex items-center gap-2 px-4 py-2 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm"
            >
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Translate button */}
        <div className="flex justify-center">
          <motion.button
            type="button"
            onClick={handleTranslate}
            disabled={loading}
            whileHover={!loading ? { scale: 1.02 } : {}}
            whileTap={!loading ? { scale: 0.98 } : {}}
            className={cn(
              "px-8 py-3 rounded-xl font-semibold flex items-center gap-2 transition-colors",
              loading
                ? "bg-zinc-600 text-zinc-400 cursor-not-allowed"
                : "bg-gradient-to-r from-[#FF416C] to-[#FF4B2B] text-white hover:shadow-lg hover:shadow-[#FF416C]/30"
            )}
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Translating…
              </>
            ) : (
              <>
                <Globe className="w-5 h-5" />
                Translate
              </>
            )}
          </motion.button>
        </div>
      </div>
    </main>
  );
}
