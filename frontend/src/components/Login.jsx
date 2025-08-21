import { useState } from "react";
import { api } from "../api";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isRegister, setIsRegister] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const endpoint = isRegister ? "/auth/register" : "/auth/login";

      const body = isRegister
        ? { email, password, name: username }
        : { email, password };

      const res = await api(endpoint, {
        method: "POST",
        body, // ✅ artık JSON.stringify burada değil, api.js içinde
      });

      if (res.access_token) {
        onLogin(res.access_token);
      } else {
        setError("İşlem başarısız. Token alınamadı.");
      }
    } catch (err) {
      console.error("API error:", err);

      let message = "İşlem başarısız";

      if (typeof err === "object") {
        if (err.msg) {
          message = err.msg;
        } else if (typeof err.message === "string") {
          message = err.message;
        } else if (typeof err.detail === "string") {
          message = err.detail;
        }
      }

      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex items-center justify-center h-screen bg-gray-100 dark:bg-gray-900">
      <form
        onSubmit={handleSubmit}
        className="bg-white dark:bg-gray-800 p-8 rounded shadow-md w-80 flex flex-col gap-4"
      >
        <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
          {isRegister ? "Kayıt Ol" : "Giriş Yap"}
        </h1>

        {error && <div className="text-red-600 text-sm">{error}</div>}

        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          className="input"
          required
        />

        {isRegister && (
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Kullanıcı adı"
            className="input"
            required
          />
        )}

        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Parola"
          className="input"
          required
        />

        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
        >
          {loading
            ? isRegister
              ? "Kayıt olunuyor..."
              : "Giriş yapılıyor..."
            : isRegister
            ? "Kayıt Ol"
            : "Giriş Yap"}
        </button>

        <button
          type="button"
          onClick={() => setIsRegister(!isRegister)}
          className="text-sm text-indigo-600 hover:underline mt-2"
        >
          {isRegister
            ? "Zaten hesabınız var mı? Giriş Yap"
            : "Hesabınız yok mu? Kayıt Ol"}
        </button>
      </form>
    </div>
  );
}
