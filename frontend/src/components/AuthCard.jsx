import { useState } from 'react'
import Logo from '../icons/Logo'
import Login from './Login'
import Register from './Register'

export default function AuthCard({ onAuthed }) {
  const [tab, setTab] = useState('login')

  return (
    <div className="max-w-md mx-auto p-6 card mt-16">
      <div className="flex items-center gap-3 mb-6">
        <Logo className="w-9 h-9"/>
        <div>
          <h1 className="text-xl font-semibold">PDF RAG Chatbot</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">PDF üzerinden sohbet — RAG + Gemma</p>
        </div>
      </div>

      <div className="flex gap-2 mb-4">
        <button onClick={() => setTab('login')} 
                className={`btn-secondary ${tab==='login'?'ring-2 ring-indigo-500':''}`}>
          Giriş
        </button>
        <button onClick={() => setTab('register')} 
                className={`btn-secondary ${tab==='register'?'ring-2 ring-indigo-500':''}`}>
          Kayıt Ol
        </button>
      </div>

      {tab === 'login' 
        ? <Login onAuthed={onAuthed} /> 
        : <Register onAuthed={onAuthed} />}
    </div>
  )
}
