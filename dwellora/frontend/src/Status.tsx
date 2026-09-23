import { useEffect, useState } from 'react';
import { API_BASE_URL } from './lib/endpoints';
export function Status(){ const [status,setStatus]=useState('Connecting'); const [last,setLast]=useState('—'); useEffect(()=>{const f=(e: Event)=>{const d=(e as CustomEvent).detail;setStatus(d.ok?'Connected':'Server Error');setLast(`${d.ms} ms`)};addEventListener('dwellora:api',f);return()=>removeEventListener('dwellora:api',f)},[]); return <div className="status"><span className={`dot ${status.toLowerCase().replace(' ','-')}`}/>{status}<small>{API_BASE_URL} · Last response {last}</small></div> }
