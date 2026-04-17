"use client";

import { useState } from "react";
import { Send, MessageSquare, X, Bot, Loader2, Zap } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [history, setHistory] = useState<{ role: "user" | "bot", text: string }[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!query.trim()) return;
    
    const userMessage = query;
    setQuery("");
    setHistory([...history, { role: "user", text: userMessage }]);
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMessage }),
      });
      const data = await res.json();
      setHistory(prev => [...prev, { role: "bot", text: data.response }]);
    } catch (err) {
      setHistory(prev => [...prev, { role: "bot", text: "Error de conexión con el motor de IA." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-gold rounded-full flex items-center justify-center shadow-lg shadow-gold/20 hover:scale-110 transition-all z-50 text-black"
      >
        <MessageSquare className="w-6 h-6" />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div 
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-24 right-6 w-[400px] h-[600px] glass-card flex flex-col z-[60] shadow-2xl overflow-hidden"
          >
            {/* Header */}
            <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/[0.02]">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-gold/10 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-gold" />
                </div>
                <div>
                  <h3 className="text-sm font-bold">Claude Intelligence</h3>
                  <p className="text-[10px] text-white/30 uppercase tracking-widest font-bold">Real Estate Expert</p>
                </div>
              </div>
              <button onClick={() => setIsOpen(false)} className="text-white/20 hover:text-white transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {history.length === 0 && (
                <div className="h-full flex flex-col items-center justify-center text-center px-4">
                  <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center mb-4">
                    <Zap className="w-6 h-6 text-gold/40" />
                  </div>
                  <p className="text-sm text-white/40 leading-relaxed">
                    Pregúntame sobre el mercado polaco 2027.<br />
                    <span className="text-[11px] mt-2 block">Ej: "3 habitaciones en Varsovia bajo 800k"</span>
                  </p>
                </div>
              )}
              {history.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                    msg.role === "user" 
                    ? "bg-gold text-black font-medium rounded-tr-none" 
                    : "bg-white/5 border border-white/10 text-white/80 rounded-tl-none"
                  }`}>
                    {msg.text.split("\n").map((line, j) => (
                      <p key={j} className={j > 0 ? "mt-2" : ""}>{line}</p>
                    ))}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-none px-4 py-3">
                    <Loader2 className="w-4 h-4 text-gold animate-spin" />
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="p-4 bg-white/[0.02] border-t border-white/10">
              <div className="relative">
                <input 
                  type="text" 
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                  placeholder="Escribe tu consulta..."
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-4 pr-12 text-sm focus:outline-none focus:border-gold/30 transition-all"
                />
                <button 
                  onClick={sendMessage}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-gold hover:scale-110 transition-transform"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
