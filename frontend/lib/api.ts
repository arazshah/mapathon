import { QueryResponse } from "@/types"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"

export async function sendQuery(question: string): Promise<QueryResponse> {
  const res = await fetch(`${BACKEND_URL}/api/v1/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  })

  if (!res.ok) {
    throw new Error(`خطای سرور: ${res.status}`)
  }

  return res.json()
}
