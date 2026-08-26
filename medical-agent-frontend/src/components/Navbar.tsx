"use client";

import Link from "next/link";
import { useAuth } from "@/components/AuthProvider";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-white shadow-lg p-4 flex justify-between items-center sticky top-0 z-50">
      <div className="flex space-x-4">
        <Link href="/chat" className="text-blue-600 hover:text-blue-800 font-medium">
          Chat
        </Link>
        <Link href="/upload" className="text-blue-600 hover:text-blue-800 font-medium">
          Upload Document
        </Link>
      </div>
      <div className="flex items-center space-x-4">
        {user && <span className="text-sm text-gray-600">{user.email}</span>}
        <button
          onClick={logout}
          className="text-red-500 hover:text-red-700 font-medium"
        >
          Logout
        </button>
      </div>
    </nav>
  );
}