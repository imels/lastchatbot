import { useState } from 'react'
import { api } from '../api'

export default function Register({ onAuthed }) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function submit(e){
    e.preventDefault()
    setLoading(true); setError(null)
    try {
      const data = await api('/auth/register', { method:'POST', body:{ name, email, password }})
      // data içinden access_token ve user bilgisi gelecek varsayımıyla:
      onAuthed({ token: data.access_token, user: data.user })
    } catch(err) { 
      setError(err.message) 
    } finally { 
      setLoading(false) 
    }
  }

  return (
    <form onSubmit={submit} className="space-y-3">
      <input className="input" placeholder="Ad Soyad" value={name} onChange={e=>setName(e.target.value)} />
      <input className="input" placeholder="E-posta" value={email} onChange={e=>setEmail(e.target.value)} />
      <input className="input" placeholder="Şifre" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
      {error && <div className="text-red-600 text-sm">{error}</div>}
      <button className="btn w-full" disabled={loading}>
        {loading ? 'Kaydediliyor...' : 'Kayıt Ol'}
      </button>
    </form>
  )
}
