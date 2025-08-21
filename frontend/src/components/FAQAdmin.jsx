import { useEffect, useState } from 'react'
import { api } from '../api'

export default function FAQAdmin({ token }) {
  const [faqs, setFaqs] = useState([])
  const [q, setQ] = useState('')
  const [a, setA] = useState('')

  async function load(){ setFaqs(await api('/faqs/', { token })) }
  useEffect(()=>{ load().catch(console.error) },[])

  async function add(){
    await api('/faqs/', { method:'POST', token, body:{ question:q, answer:a, tags:[] } })
    setQ(''); setA(''); load().catch(console.error)
  }
  async function del(id){
    await api(`/faqs/${id}`, { method:'DELETE', token })
    load().catch(console.error)
  }

  return (
    <div className="card p-4">
      <h3 className="font-semibold mb-2">SSS Yönetimi</h3>
      <div className="flex gap-2 mb-2">
        <input className="input" placeholder="Soru" value={q} onChange={e=>setQ(e.target.value)} />
        <input className="input" placeholder="Cevap" value={a} onChange={e=>setA(e.target.value)} />
        <button className="btn" onClick={add}>Ekle</button>
      </div>
      <ul className="space-y-2">
        {faqs.map(f=>(
          <li key={f.id} className="flex items-center justify-between">
            <div>
              <div className="font-medium">{f.question}</div>
              <div className="text-sm text-gray-500">{f.answer}</div>
            </div>
            <button onClick={()=>del(f.id)} className="btn-secondary">Sil</button>
          </li>
        ))}
      </ul>
    </div>
  )
}
