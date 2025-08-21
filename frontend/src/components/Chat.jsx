import { useState, useEffect, useRef } from "react";
import { api } from "../api";
import UploadPDF from "./UploadPDF";

export default function Chat({ token, session }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const messagesEndRef = useRef(null);

  // Mesaj listesini scroll etmek için
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (!session) return;
    async function fetchHistory() {
      try {
        const res = await api(`/chat/history/${session.id}`, { method: "GET", token });
        setMessages(res);
      } catch (err) {
        console.error(err);
      }
    }
    fetchHistory();
  }, [session, token]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  async function sendMessage() {
    if (!input.trim() || !session) return;

    // Kullanıcının mesajını anında göster
    const userMsg = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const payload = { session_id: session.id, content: input };
      const res = await api("/chat/ask", { method: "POST", token, body: payload });

      const assistantMsg = { role: "assistant", content: res.answer };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error(err);
      // Hata mesajını göster
      setMessages((prev) => [...prev, { role: "assistant", content: "Mesaj gönderilemedi. Backend çalışıyor mu?" }]);
    } finally {
      setLoading(false);
    }
  }

  if (!session)
    return (
      <div className="flex-1 flex items-center justify-center text-gray-500">
        Lütfen bir sohbet seçin
      </div>
    );

  return (
    <div className="flex-1 flex flex-col p-2">
      <div className="flex-1 overflow-y-auto mb-2 space-y-2">
        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "text-right" : "text-left"}>
            <div
              className={`inline-block px-3 py-1 rounded ${
                m.role === "user" ? "bg-blue-500 text-white" : "bg-gray-300 text-black"
              }`}
            >
              {m.content}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          className="flex-1 px-2 py-1 border rounded"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Mesajınızı yazın..."
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button
          onClick={sendMessage}
          className="px-3 py-1 bg-green-600 text-white rounded"
          disabled={loading}
        >
          {loading ? "Gönderiliyor..." : "Gönder"}
        </button>
        <button
          onClick={() => setShowUpload(true)}
          className="px-3 py-1 bg-gray-500 text-white rounded"
        >
          PDF Yükle
        </button>
      </div>

      {showUpload && <UploadPDF token={token} session={session} onClose={() => setShowUpload(false)} />}
    </div>
  );
}
