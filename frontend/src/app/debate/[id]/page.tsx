"use client";

import { useState, useRef, useEffect, use } from "react";
import { submitTurn, scoreDebate } from "@/lib/api-client";
import ScorePanel from "@/components/ScorePanel";

type Citation = { section_number: string; snippet: string };
type Turn = { id: string; role: 'student' | 'counsel'; content: string; citations?: Citation[] };

export default function DebateChat({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const debateId = resolvedParams.id;
  const [turns, setTurns] = useState<Turn[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [scoring, setScoring] = useState(false);
  const [score, setScore] = useState<any>(null);
  
  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading || score) return;
    
    const userTurn: Turn = { id: Date.now().toString(), role: 'student', content: input };
    setTurns(prev => [...prev, userTurn]);
    setInput("");
    setLoading(true);
    
    try {
      const res = await submitTurn(debateId, input);
      const aiTurn: Turn = { 
        id: res.turn_id, 
        role: 'counsel', 
        content: res.counter_argument,
        citations: res.citations
      };
      setTurns(prev => [...prev, aiTurn]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleEndDebate = async () => {
    setScoring(true);
    try {
      const res = await scoreDebate(debateId);
      setScore(res);
    } catch (err) {
      console.error(err);
    } finally {
      setScoring(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col max-w-4xl mx-auto p-4">
      <header className="py-4 border-b border-slate-800 flex justify-between items-center">
        <h1 className="text-xl font-bold text-white">Opposing Counsel</h1>
        <button 
          onClick={handleEndDebate}
          disabled={loading || scoring || score !== null || turns.length === 0}
          className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
        >
          {scoring ? "Scoring..." : "End Debate"}
        </button>
      </header>

      <main className="flex-1 overflow-y-auto py-6 space-y-6">
        {turns.map((turn) => (
          <div key={turn.id} className={`flex ${turn.role === 'student' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-2xl p-4 ${turn.role === 'student' ? 'bg-indigo-600 text-white rounded-br-none' : 'bg-slate-800 border border-slate-700 text-slate-200 rounded-bl-none'}`}>
              <p className="whitespace-pre-wrap">{turn.content}</p>
              
              {turn.citations && turn.citations.length > 0 && (
                <div className="mt-4 space-y-2">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Citations</p>
                  {turn.citations.map((c, i) => (
                    <details key={i} className="bg-slate-900 rounded-lg border border-slate-700 overflow-hidden cursor-pointer group">
                      <summary className="p-2 text-sm font-medium text-indigo-400 group-hover:text-indigo-300 focus:outline-none">
                        Section {c.section_number}
                      </summary>
                      <div className="p-3 bg-slate-900 border-t border-slate-800 text-sm text-slate-300">
                        {c.snippet}
                      </div>
                    </details>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 border border-slate-700 rounded-2xl rounded-bl-none p-4 max-w-[80%]">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={endOfMessagesRef} />
      </main>

      {score && <ScorePanel score={score} />}

      {!score && (
        <footer className="pt-4 border-t border-slate-800">
          <form onSubmit={handleSend} className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="State your argument..."
              disabled={loading}
              className="flex-1 bg-slate-800 border border-slate-700 text-white rounded-lg p-3 outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              Send
            </button>
          </form>
        </footer>
      )}
    </div>
  );
}
