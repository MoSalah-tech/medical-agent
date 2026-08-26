"use client";

import { useState } from "react";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useAuth } from "@/components/AuthProvider";
import { uploadDocument } from "@/lib/api";
import { FileUploadResponse } from "@/types";

export default function UploadPage() {
  const { token } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleUpload = async () => {
    if (!file || !token) return;
    setUploading(true);
    setMessage("");
    setError("");
    try {
      const result: FileUploadResponse = await uploadDocument(token, file);
      setMessage(`Uploaded successfully! ${result.chunks_ingested} chunks ingested.`);
    } catch (err: any) {
      setError(`Error: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="max-w-2xl mx-auto">
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-8">
          <h1 className="text-2xl font-bold text-gray-800 mb-6">Upload Medical Document</h1>
          <p className="text-sm text-gray-600 mb-4">
            Supported formats: PDF, DOCX, TXT, PNG, JPG, JPEG, TIFF, BMP
          </p>
          <input
            type="file"
            accept=".pdf,.docx,.txt,.text,.png,.jpg,.jpeg,.tiff,.bmp"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="mb-4 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100"
          />
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="bg-purple-600 text-white px-6 py-2 rounded-xl hover:bg-purple-700 disabled:opacity-50"
          >
            {uploading ? "Uploading..." : "Upload"}
          </button>
          {message && <p className="mt-4 text-green-600">{message}</p>}
          {error && <p className="mt-4 text-red-600">{error}</p>}
        </div>
      </div>
    </ProtectedRoute>
  );
}