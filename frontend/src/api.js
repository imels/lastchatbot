const API_URL = "http://127.0.0.1:8000"; // local backend

export const api = async (endpoint, options = {}) => {
  try {
    const headers = options.headers ? { ...options.headers } : {};

    // Token ekle
    if (options.token) {
      headers["Authorization"] = `Bearer ${options.token}`;
    }

    let body = options.body;

    // JSON değilse form-data gönder
    if (!options.isForm) {
      headers["Content-Type"] = "application/json";
      body = options.body ? JSON.stringify(options.body) : undefined;
    }

    const res = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
      body,
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      throw data; // Backend’den gelen hata objesi
    }

    return data;
  } catch (err) {
    console.error("API error:", err);
    throw err.detail || err.message || "Bilinmeyen hata";
  }
};
