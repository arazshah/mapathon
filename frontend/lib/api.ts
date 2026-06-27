import { QueryResponse } from "@/types"

// آدرس بک‌اند از متغیر محیطی
export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function sendQuery(question: string): Promise<QueryResponse> {
  const res = await fetch(`${API_URL}/api/v1/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  })

  if (!res.ok) {
    throw new Error(`خطای سرور: ${res.status}`)
  }

  return res.json()
}
