"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/components/AuthProvider";
import { listConversations, deleteConversation } from "@/lib/api";
import { Conversation } from "@/types";

interface Props {
  activeSessionId: string | null;
  onSelect: (conversationId: string, sessionId: string) => void;
  onNewChat: () => void;
}

export default function ChatSidebar({ activeSessionId, onSelect, onNewChat }: Props) {
  const { token } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  const loadConversations = async () => {
    if (!token) return;
    try {
      const data = await listConversations(token);
      setConversations(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, [token]);

  const handleDelete = async (id: string) => {
    if (!token) return;
    try {
      await deleteConversation(token, id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeSessionId === id) onNewChat();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="w-full md:w-64 bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-4 h-full overflow-y-auto">
      <button
        onClick={onNewChat}
        className="w-full mb-4 bg-blue-600 text-white py-2 rounded-xl hover:bg-blue-700 transition"
      >
        + New Chat
      </button>
      <div className="space-y-2">
        {loading && <p className="text-gray-500 text-sm">Loading...</p>}
        {!loading && conversations.length === 0 && (
          <p className="text-gray-500 text-sm">No conversations yet.</p>
        )}
        {conversations.map((conv) => (
          <div
            key={conv.id}
            className={`p-2 rounded-xl cursor-pointer flex justify-between items-center ${
              activeSessionId === conv.session_id ? "bg-blue-100" : "hover:bg-gray-100"
            }`}
            onClick={() => onSelect(conv.id, conv.session_id)}
          >
            <span className="text-sm truncate">
              {conv.title || new Date(conv.created_at).toLocaleDateString()}
            </span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleDelete(conv.id);
              }}
              className="text-red-500 hover:text-red-700"
            >
              🗑
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}