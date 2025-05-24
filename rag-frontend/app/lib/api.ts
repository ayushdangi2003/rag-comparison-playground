import axios from "axios";

const API_BASE = "http://localhost:8000";

export async function queryRAG(type: "query" | "selfquery" | "rerank", query: string) {
  const res = await axios.post(`${API_BASE}/${type}`, { query });
  return res.data;
}
