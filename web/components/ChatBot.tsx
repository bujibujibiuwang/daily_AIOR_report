"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const SUGGESTIONS = [
  "最近有哪些VRP相关论文？",
  "供应链优化的最新进展？",
  "强化学习用于调度问题？",
  "库存管理有哪些新方法？",
];

export default function ChatBot() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "你好！我是 AI+OR 研究助手 🔬\n\n我可以基于论文库回答你的问题，例如：\n• 最近有哪些VRP相关论文？\n• 强化学习在调度问题的最新进展？\n• 供应链优化有哪些新方法？",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async (text?: string) => {
    const q = (text ?? input).trim();
    if (!q || loading) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setLoading(true);

    try {
      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const data = await resp.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.answer ?? "抱歉，未能获取回答。" },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "抱歉，请求失败，请检查网络后重试。" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setOpen((v) => !v)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-br from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-full shadow-xl text-2xl flex items-center justify-center transition-transform hover:scale-110 z-50"
        title="AI 研究助手"
      >
        {open ? "✕" : "💬"}
      </button>

      {/* Chat window */}
      {open && (
        <div className="fixed bottom-24 right-6 w-96 h-[520px] bg-white rounded-2xl shadow-2xl border border-gray-100 flex flex-col z-50 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-3 flex items-center justify-between">
            <div>
              <h3 className="font-bold text-sm">🤖 AI+OR 研究助手</h3>
              <p className="text-xs text-blue-200">基于论文库的智能问答</p>
            </div>
            <button
              onClick={() =>
                setMessages([
                  {
                    role: "assistant",
                    content: "对话已清空，请继续提问 😊",
                  },
                ])
              }
              className="text-xs text-blue-200 hover:text-white"
            >
              清空
            </button>
          </div>

          {/* Quick suggestions */}
          {messages.length === 1 && (
            <div className="px-3 pt-2 flex flex-wrap gap-1.5">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 px-2.5 py-1 rounded-full transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {m.role === "assistant" && (
                  <span className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 text-white text-xs flex items-center justify-center mr-2 shrink-0 mt-1">
                    🤖
                  </span>
                )}
                <div
                  className={`max-w-[78%] px-3 py-2 rounded-2xl text-sm whitespace-pre-wrap leading-relaxed ${
                    m.role === "user"
                      ? "bg-blue-600 text-white rounded-br-sm"
                      : "bg-gray-100 text-gray-800 rounded-bl-sm"
                  }`}
                >
                  {m.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start items-center gap-2">
                <span className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 text-xs flex items-center justify-center text-white">
                  🤖
                </span>
                <div className="bg-gray-100 px-3 py-2 rounded-2xl rounded-bl-sm">
                  <span className="flex gap-1">
                    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
                    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
                    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
                  </span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="p-3 border-t flex gap-2 bg-gray-50">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
              placeholder="输入问题，Enter 发送..."
              className="flex-1 border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white"
            />
            <button
              onClick={() => send()}
              disabled={loading || !input.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors"
            >
              发送
            </button>
          </div>
        </div>
      )}
    </>
  );
}
