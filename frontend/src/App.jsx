import { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import Login from "./components/Login";
import Chat from "./components/Chat";

export default function App() {
  const [token, setToken] = useState(null);
  const [currentSession, setCurrentSession] = useState(null);

  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    if (savedToken) setToken(savedToken);
  }, []);

  function handleLogin(t) {
    setToken(t);
    localStorage.setItem("token", t);
  }

  function handleLogout() {
    setToken(null);
    setCurrentSession(null);
    localStorage.removeItem("token");
  }

  if (!token) return <Login onLogin={handleLogin} />;

  return (
    <div className="flex h-screen">
      <Sidebar token={token} currentId={currentSession?.id} onSelectSession={setCurrentSession} />
      <div className="flex-1 flex flex-col">
        <div className="p-2 border-b border-gray-200 dark:border-gray-700 flex justify-end">
          <button
            onClick={handleLogout}
            className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Çıkış Yap
          </button>
        </div>
        <Chat token={token} session={currentSession} />
      </div>
    </div>
  );
}
