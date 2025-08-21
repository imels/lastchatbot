import { useEffect, useState } from "react";
import { api } from "../api";

export default function Sidebar({ token, currentId, onSelectSession }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [newTitle, setNewTitle] = useState(""); // Kullanıcıdan sohbet adı al

  // Sohbetleri yükle
  async function fetchSessions() {
    setLoading(true);
    setError("");
    try {
      const res = await api("/session/list", { method: "GET", token });
      setSessions(res.map(s => ({ id: s.id || s._id, title: s.title })));
    } catch (err) {
      console.error(err);
      setError(err.message || "Sohbetler yüklenemedi");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (token) fetchSessions();
  }, [token]);

  // Yeni sohbet oluştur
  async function newSession() {
    if (!newTitle.trim()) {
      setError("Lütfen bir sohbet başlığı girin");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const form = new FormData();
      form.append("title", newTitle.trim());

      const res = await api("/session/", {
        method: "POST",
        token,
        body: form,
        isForm: true,
      });

      const sessionObj = { id: res.id || res._id, title: res.title };
      setSessions([sessionObj, ...sessions]);
      onSelectSession(sessionObj);

      setNewTitle(""); // input temizle
    } catch (err) {
      console.error(err);
      setError(err.detail || err.message || "Yeni sohbet oluşturulamadı");
    } finally {
      setLoading(false);
    }
  }

  // Sohbet sil
  async function deleteSession(id) {
    if (!window.confirm("Bu sohbeti silmek istediğinize emin misiniz?")) return;
    setLoading(true);
    setError("");
    try {
      await api(`/session/delete/${id}`, { method: "DELETE", token });
      await fetchSessions(); // Silme sonrası güncel listeyi çek
      if (currentId === id) onSelectSession(null);
    } catch (err) {
      console.error(err);
      setError(err.detail || err.message || "Sohbet silinemedi");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-64 bg-gray-200 dark:bg-gray-800 p-2 flex flex-col gap-2">
      {/* Yeni sohbet input */}
      <div className="flex gap-2 mb-2">
        <input
          type="text"
          className="flex-1 px-2 py-1 rounded border border-gray-400 dark:border-gray-600 text-sm"
          placeholder="Yeni sohbet başlığı"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
        />
        <button
          onClick={newSession}
          className="px-2 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 text-xs flex-shrink-0"
        >
          Oluştur
        </button>
      </div>

      {error && <div className="text-red-600 text-sm">{error}</div>}
      {loading && <div className="text-gray-700 dark:text-gray-200 text-sm">Yükleniyor...</div>}

      <div className="flex-1 overflow-y-auto mt-2">
        {sessions.map((s) => (
          <div
            key={s.id}
            className={`p-2 rounded cursor-pointer flex justify-between items-center ${
              currentId === s.id
                ? "bg-indigo-500 text-white"
                : "hover:bg-indigo-300 dark:hover:bg-indigo-600"
            }`}
          >
            <span onClick={() => onSelectSession(s)}>
              {s.title || `Sohbet ${s.id}`}
            </span>
            <button
              onClick={() => deleteSession(s.id)}
              className="ml-2 text-red-600 hover:text-red-800 flex-shrink-0"
            >
              Sil
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
