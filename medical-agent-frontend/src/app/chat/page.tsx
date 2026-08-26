"use client";

import { useState, useRef } from "react";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useAuth } from "@/components/AuthProvider";
import ChatSidebar from "@/components/ChatSidebar";
import { sendChatMessage, sendVoiceMessage, getConversationMessages } from "@/lib/api";
import { ChatResponse } from "@/types";
import ReactMarkdown from "react-markdown";

interface Message {
  role: "user" | "assistant";
  content: string;
  citations?: string[];
}

export default function ChatPage() {
  const { token } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const handleNewChat = () => {
    setMessages([]);
    setSessionId(null);
    setConversationId(null);
  };

  const handleSelectConversation = async (convId: string, sessId: string) => {
    if (!token) return;
    try {
      const history = await getConversationMessages(token, convId);
      const formatted = history.map((msg: any) => ({
        role: msg.role,
        content: msg.content,
      }));
      setMessages(formatted);
      setSessionId(sessId);
      setConversationId(convId);
    } catch (error) {
      console.error("Failed to load messages", error);
      alert("Could not load messages for this conversation.");
    }
  };

  const handleSendText = async () => {
    if (!input.trim() || !token) return;
    const userMsg: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const response: ChatResponse = await sendChatMessage(token, input, sessionId);
      const assistantMsg: Message = {
        role: "assistant",
        content: response.response,
        citations: response.citations,
      };
      setMessages((prev) => [...prev, assistantMsg]);
      if (response.conversation_id) setConversationId(response.conversation_id);
      if (response.session_id) setSessionId(response.session_id);
    } catch (error: any) {
      const errMsg: Message = { role: "assistant", content: `Error: ${error.message}` };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      let options: MediaRecorderOptions = {};
      if (MediaRecorder.isTypeSupported("audio/webm")) {
        options = { mimeType: "audio/webm" };
      } else if (MediaRecorder.isTypeSupported("audio/mp4")) {
        options = { mimeType: "audio/mp4" };
      }
      const mediaRecorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const mimeType = mediaRecorder.mimeType || "audio/webm";
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        await handleSendVoice(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setRecording(true);
    } catch (err) {
      console.error("Microphone access denied", err);
      alert("Unable to access microphone. Please allow microphone permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  const handleSendVoice = async (audioBlob: Blob) => {
    if (!token) return;
    const userMsg: Message = { role: "user", content: "🎤 Voice message" };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    try {
      const response: ChatResponse = await sendVoiceMessage(token, audioBlob, sessionId);
      const assistantMsg: Message = {
        role: "assistant",
        content: response.response,
        citations: response.citations,
      };
      setMessages((prev) => [...prev, assistantMsg]);
      if (response.conversation_id) setConversationId(response.conversation_id);
      if (response.session_id) setSessionId(response.session_id);
    } catch (error: any) {
      const errMsg: Message = { role: "assistant", content: `Error: ${error.message}` };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="flex flex-col md:flex-row h-[calc(100vh-4rem)] gap-4">
  <div className="w-full md:w-64">
    <ChatSidebar
      activeSessionId={sessionId}
      onSelect={handleSelectConversation}
      onNewChat={handleNewChat}
    />
  </div>
  <div className="flex-1 bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl overflow-hidden flex flex-col">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 mt-8">Start a conversation...</div>
            )}
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`max-w-[75%] p-3 rounded-2xl ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white ml-auto"
                    : "bg-gray-100 text-gray-800 mr-auto"
                }`}
              >
                {msg.role === "assistant" ? (
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                ) : (
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                )}
                {msg.citations && msg.citations.length > 0 && (
                  <p className="text-xs text-gray-500 mt-1">
                    Sources: {msg.citations.join(", ")}
                  </p>
                )}
              </div>
            ))}
            {loading && <div className="text-center text-gray-500 text-sm">Thinking...</div>}
          </div>
          <div className="p-4 bg-gray-50 flex flex-col sm:flex-row gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendText()}
              className="flex-1 border border-gray-300 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
              placeholder="Describe your symptoms..."
            />
            <button
              onClick={handleSendText}
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded-xl hover:bg-blue-700 disabled:opacity-50"
            >
              Send
            </button>
            <button
              onClick={recording ? stopRecording : startRecording}
              className={`px-4 py-2 rounded-xl text-white ${
                recording ? "bg-red-500 hover:bg-red-600" : "bg-green-500 hover:bg-green-600"
              }`}
            >
              {recording ? "Stop" : "🎤"}
            </button>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}