"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createDebate } from "@/lib/api-client";

export default function NewDebate() {
  const router = useRouter();
  const [topic, setTopic] = useState("");
  const [position, setPosition] = useState<"for" | "against">("for");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic) return;
    setLoading(true);
    try {
      const debate = await createDebate(topic, position);
      router.push(`/debate/${debate.debate_id}`);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-slate-800 p-8 rounded-xl shadow-2xl border border-slate-700">
        <h1 className="text-3xl font-bold mb-6 text-center text-white">Start Practice</h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Debate Topic</label>
            <input
              type="text"
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-indigo-500 outline-none"
              placeholder="e.g. Fraud in Contracts"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Your Position</label>
            <div className="flex gap-4">
              <label className="flex-1 cursor-pointer">
                <input
                  type="radio"
                  name="position"
                  value="for"
                  checked={position === "for"}
                  onChange={() => setPosition("for")}
                  className="peer sr-only"
                />
                <div className="p-3 text-center rounded-lg border border-slate-700 peer-checked:bg-indigo-600 peer-checked:border-indigo-500 transition-colors">
                  For
                </div>
              </label>
              <label className="flex-1 cursor-pointer">
                <input
                  type="radio"
                  name="position"
                  value="against"
                  checked={position === "against"}
                  onChange={() => setPosition("against")}
                  className="peer sr-only"
                />
                <div className="p-3 text-center rounded-lg border border-slate-700 peer-checked:bg-indigo-600 peer-checked:border-indigo-500 transition-colors">
                  Against
                </div>
              </label>
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-4 rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? "Starting..." : "Begin Debate"}
          </button>
        </form>
      </div>
    </div>
  );
}
