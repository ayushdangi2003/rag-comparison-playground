"use client";

import { useState } from "react";
import { queryRAG } from "../lib/api";
import { uploadPDF } from "../lib/upload";
const ragOptions = [
  { id: "query", label: "Simple RAG" },
  { id: "selfquery", label: "Self-Query RAG" },
  { id: "rerank", label: "RAG + Reranker" },
];

export default function CompareView() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);
  const [results, setResults] = useState<Record<string, any>>({});
  const [file, setFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState("");

  const toggle = (id: string) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const runQuery = async () => {
    setLoading(true);
    const allResults: Record<string, any> = {};

    for (const id of selected) {
      try {
        const res = await queryRAG(id as any, query);
        allResults[id] = res;
      } catch (err) {
        allResults[id] = { error: "Failed" };
      }
    }

    setResults(allResults);
    setLoading(false);
  };

  return (
    <>
      <div className="bg-gray-100 p-4 mb-6 rounded shadow text-center">
        <h2 className="text-2xl font-semibold mb-1 text-black">👨‍💻 Ayush Dangi</h2>
        <p className="mb-2 text-gray-800">
          3rd Year CSE at PES University 
        </p>
        <a
          href="https://github.com/ayushdangi2003/AyushDangiResume.pdf"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block px-5 py-2 bg-black text-white rounded hover:bg-gray-800"
        >
          📄 View My Resume
        </a>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-10">
        <h1 className="text-3xl font-bold mb-6">RAG Comparison Playground</h1>
        <div className="mb-4">
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <button
            onClick={async () => {
              if (!file) return;
              setUploadStatus("Uploading...");
              try {
                const res = await uploadPDF(file);
                setUploadStatus("✅ " + res.message);
              } catch {
                setUploadStatus("❌ Upload failed");
              }
            }}
            className="ml-2 px-4 py-2 bg-purple-600 text-white rounded"
          >
            Upload PDF
          </button>
          {uploadStatus && <p className="text-sm mt-1">{uploadStatus}</p>}
        </div>
        <textarea
          className="w-full p-4 border rounded mb-4 text-black"
          placeholder="Enter your query..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />

        <div className="flex flex-wrap gap-4 mb-4">
          {ragOptions.map((opt) => (
            <button
              key={opt.id}
              className={`px-4 py-2 border rounded ${
                selected.includes(opt.id)
                  ? "bg-blue-600 text-white"
                  : "bg-white text-black"
              }`}
              onClick={() => toggle(opt.id)}
            >
              {opt.label}
            </button>
          ))}
        </div>

        <button
          onClick={runQuery}
          disabled={loading || selected.length === 0 || !query}
          className="bg-green-600 text-white px-6 py-2 rounded disabled:opacity-50"
        >
          {loading ? "Running..." : "Compare"}
        </button>

        {Object.keys(results).length > 0 && (
          <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-4">
            {selected.map((id) => (
              <div key={id} className="p-4 border rounded shadow bg-white">
                <h2 className="font-semibold text-lg mb-2">
                  {ragOptions.find((r) => r.id === id)?.label}
                </h2>
                <div>
                  <strong>Answer:</strong>
                  <p className="mb-2 text-black">{results[id]?.answer || "N/A"}</p>

                  <strong>Sources:</strong>
                  <ul className="text-sm list-disc ml-5">
                    {(results[id]?.sources || results[id]?.reranked_sources || []).map(
                      (chunk: string, i: number) => (
                        <li key={i}>{chunk.slice(0, 120)}...</li>
                      )
                    )}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
