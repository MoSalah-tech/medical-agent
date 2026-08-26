import { TokenResponse, ChatResponse, FileUploadResponse, Conversation } from "@/types";
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function registerUser(email: string, password: string, fullName?: string) {
  const res = await fetch(`${API_URL}/api/v1/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name: fullName }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Registration failed");
  }
  return res.json();
}

export async function loginUser(email: string, password: string) {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  const res = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData.toString(),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Login failed");
  }
  return res.json() as Promise<TokenResponse>;
}



export async function listConversations(token: string) {
  const res = await fetch(`${API_URL}/api/v1/chat/conversations`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to load conversations");
  return res.json() as Promise<Conversation[]>;
}

export async function deleteConversation(token: string, id: string) {
  const res = await fetch(`${API_URL}/api/v1/chat/conversations/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to delete conversation");
  return res.json();
}
export async function getConversationMessages(token: string, conversationId: string) {
  const res = await fetch(`${API_URL}/api/v1/chat/conversations/${conversationId}/messages`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    throw new Error("Failed to load messages");
  }
  return res.json(); // returns array of {role, content}
} 

export async function sendChatMessage(token: string, text: string, sessionId?: string | null) {
  const res = await fetch(`${API_URL}/api/v1/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ text, session_id: sessionId || null }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Chat failed");
  }
  return res.json() as Promise<ChatResponse>;
}

export async function sendVoiceMessage(token: string, audioBlob: Blob, sessionId?: string | null) {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.webm");
  if (sessionId) formData.append("session_id", sessionId);

  const res = await fetch(`${API_URL}/api/v1/voice`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Voice chat failed");
  }
  return res.json() as Promise<ChatResponse>;
}

export async function uploadDocument(token: string, file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_URL}/api/v1/files/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Upload failed");
  }
  return res.json() as Promise<FileUploadResponse>;
}