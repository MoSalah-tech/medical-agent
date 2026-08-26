export interface User {
  id: string;
  email: string;
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface ChatResponse {
  response: string;
  citations: string[];
  conversation_id?: string;
  session_id?: string;
}

export interface FileUploadResponse {
  message: string;
  chunks_ingested: number;
}


export interface Conversation {
  id: string;
  session_id: string;
  title: string | null;
  created_at: string;
  updated_at: string | null;
}