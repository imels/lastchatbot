import { useState } from "react";
import { api } from "../api";

export default function UploadPDF({ token, session, onClose, onUploaded }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState(null);

  async function upload() {
    if (!file) {
      setMsg("Lütfen bir PDF dosyası seçin.");
      return;
    }

    if (!session || !session.id) {
      setMsg("Geçerli bir oturum bulunamadı.");
      return;
    }

    setLoading(true);
    setMsg(null);

    const form = new FormData();
    form.append("pdf", file);

    try {
      const res = await api(`/session/${session.id}/upload`, {
        method: "POST",
        token,
        body: form,
        isForm: true,
      });

      setMsg(`Yüklendi! ${res.chunks || 0} parça indekslendi.`);

      // Opsiyonel: PDF yüklendikten sonra chat component’i bilgilendir
      if (onUploaded) onUploaded(res);
    } catch (err) {
      console.error(err);
      setMsg("Hata: " + (err.detail || err.message || "PDF yüklenemedi. Backend çalışıyor mu?"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
      <div className="card w-full max-w-md p-4 bg-white dark:bg-gray-800 rounded">
        <h3 className="font-semibold mb-2">
          PDF Yükle — {session?.title || "Oturum seçin"}
        </h3>
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <div className="mt-3 flex gap-2">
          <button
            onClick={upload}
            className="btn bg-green-600 text-white rounded px-3 py-1"
            disabled={loading || !file || !session?.id}
          >
            {loading ? "Yükleniyor..." : "Yükle"}
          </button>
          <button
            onClick={onClose}
            className="btn-secondary px-3 py-1 rounded bg-gray-400 text-white"
          >
            Kapat
          </button>
        </div>
        {msg && <div className="mt-2 text-sm text-red-600">{msg}</div>}
      </div>
    </div>
  );
}
