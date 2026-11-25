import { useEffect, useMemo, useState, type FormEvent } from 'react';
import { ApiError, api, clearSession } from './lib/api';
import { create, remove } from './lib/services';
import { endpoints } from './lib/endpoints';
import { useRecords } from './hooks/useRecords';
import type { ApiRecord, Profile } from './types/api';

const configs = {
  properties: { label: 'Properties', fields: ['title', 'property_type', 'region', 'city', 'furnished', 'parking', 'water_available', 'internet_available', 'kitchen_available'] },
  services: { label: 'Service providers', fields: ['service_type', 'description'] },
  bookings: { label: 'Bookings', fields: ['hostel', 'start_date', 'end_date'] },
  accounts: { label: 'My profile', fields: [] },
} as const;
type Resource = keyof typeof configs;

const regions = ['Ahafo','Ashanti','Bono','Bono East','Central','Eastern','Greater Accra','North East','Northern','Oti','Savannah','Upper East','Upper West','Volta','Western','Western North'];
const propertyTypes = ['Apartment','Hotel','House','Hostel'];
const serviceTypes = ['Landlord / Landlady','Real-estate agent','Hotel owner','Hostel administrator','Architect','Builder / Mason','Plumber','Painter','Electrician','Welder','Cleaner','Moving service','Landscaper','Security installer','AC technicians','Other service providers'];

function errorMessage(error: unknown): string {
  if (error instanceof ApiError && error.details && typeof error.details === 'object') {
    const details = error.details as Record<string, unknown>;
    const first = Object.values(details)[0];
    if (Array.isArray(first) && typeof first[0] === 'string') return first[0];
    if (typeof first === 'string') return first;
  }
  return error instanceof Error ? error.message : 'Something went wrong. Please try again.';
}

function AuthScreen({ onAuthenticated }: { onAuthenticated: () => Promise<void> }) {
  const [mode, setMode] = useState<'login'|'register'>('login');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [bio, setBio] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      if (mode === 'register') {
        await api.post<ApiRecord>(endpoints.accounts.create, { username, email, password, bio });
      }
      const tokens = await api.post<{access:string;refresh:string}>('/auth/token/', { username, password });
      localStorage.setItem('dwellora_token', tokens.access);
      localStorage.setItem('dwellora_refresh', tokens.refresh);
      await onAuthenticated();
    } catch (caught) {
      setError(errorMessage(caught));
      if (mode === 'register') clearSession();
    } finally {
      setBusy(false);
    }
  }

  return <div className="auth-page">
    <section className="auth-story">
      <div className="auth-brand"><span>DW</span><strong>Dwellora</strong></div>
      <div className="auth-story-copy">
        <p className="eyebrow">A clearer property experience</p>
        <h1>Make better property decisions.</h1>
        <p>One place to manage property information, connect with service providers and build a more transparent housing experience in Ghana.</p>
        <div className="auth-points">
          <div><span>01</span><p><strong>Clear information</strong><small>Keep property and service details organised.</small></p></div>
          <div><span>02</span><p><strong>Account-level control</strong><small>Your profile and provider information stay connected to your account.</small></p></div>
          <div><span>03</span><p><strong>Built to improve</strong><small>Feedback and verified experiences will shape future releases.</small></p></div>
        </div>
      </div>
      <p className="auth-footnote">Dwellora · Ghana property workspace</p>
    </section>
    <section className="auth-panel">
      <div className="auth-card">
        <p className="eyebrow">{mode === 'login' ? 'Welcome back' : 'Join Dwellora'}</p>
        <h2>{mode === 'login' ? 'Sign in to your workspace' : 'Create your account'}</h2>
        <p className="muted">{mode === 'login' ? 'Use your Dwellora account to continue.' : 'Start with your personal account. You can add provider details later.'}</p>
        <form className="auth-form" onSubmit={submit}>
          <label>Username<input autoComplete="username" value={username} onChange={event=>setUsername(event.target.value)} required /></label>
          {mode === 'register' && <>
            <label>Email address<input type="email" autoComplete="email" value={email} onChange={event=>setEmail(event.target.value)} required /></label>
            <label>About you<input maxLength={100} value={bio} onChange={event=>setBio(event.target.value)} placeholder="A short profile description" required /></label>
          </>}
          <label>Password<input type="password" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} value={password} onChange={event=>setPassword(event.target.value)} required minLength={8} /></label>
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="auth-submit" disabled={busy}>{busy ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}</button>
        </form>
        <div className="auth-switch"><span>{mode === 'login' ? 'New to Dwellora?' : 'Already have an account?'}</span><button type="button" className="text-button" onClick={()=>{setMode(mode === 'login' ? 'register' : 'login');setError('');}}>{mode === 'login' ? 'Create account' : 'Sign in'}</button></div>
        <p className="auth-legal">Use accurate information and keep your account credentials private.</p>
      </div>
    </section>
  </div>;
}

function Editor({resource,onDone}:{resource:Resource;onDone:()=>void}) {
  const fields = configs[resource].fields;
  const [form,setForm] = useState<ApiRecord>({});
  const [error,setError] = useState('');
  const [busy,setBusy] = useState(false);

  function setField(field:string,value:unknown) {
    setForm(current=>({...current,[field]:value}));
  }
  function label(field:string) {
    return field.replaceAll('_',' ').replace(/\b\w/g,letter=>letter.toUpperCase());
  }
  function fieldControl(field:string) {
    const options = field === 'property_type' ? propertyTypes : field === 'region' ? regions : field === 'service_type' ? serviceTypes : null;
    if (options) return <select value={String(form[field] ?? '')} onChange={event=>setField(field,event.target.value)} required><option value="">Select {label(field).toLowerCase()}</option>{options.map(option=><option key={option} value={option}>{option}</option>)}</select>;
    if (field === 'description') return <textarea rows={4} value={String(form[field] ?? '')} onChange={event=>setField(field,event.target.value)} required />;
    if (['furnished','parking','water_available','internet_available','kitchen_available'].includes(field)) return <span className="toggle-field"><input type="checkbox" checked={Boolean(form[field])} onChange={event=>setField(field,event.target.checked)} /><span>Yes</span></span>;
    const inputType = field.includes('date') ? 'date' : field === 'hostel' ? 'number' : 'text';
    return <input type={inputType} value={String(form[field] ?? '')} onChange={event=>setField(field,field === 'hostel' ? Number(event.target.value) : event.target.value)} required={field !== 'city'} />;
  }

  async function submit(event:FormEvent<HTMLFormElement>) {
    event.preventDefault();setBusy(true);setError('');
    try { await create(resource,form);onDone(); }
    catch(caught) { setError(errorMessage(caught)); }
    finally { setBusy(false); }
  }

  return <form className="editor" onSubmit={submit}>
    <div className="editor-heading"><p className="eyebrow">New record</p><h3>Add {configs[resource].label.replace(/s$/,'')}</h3></div>
    <div className="editor-fields">{fields.map(field=><label key={field}>{label(field)}{fieldControl(field)}</label>)}</div>
    {error && <p className="form-error" role="alert">{error}</p>}
    <div className="editor-actions"><button type="button" className="secondary" onClick={onDone}>Cancel</button><button disabled={busy}>{busy?'Saving…':'Save record'}</button></div>
  </form>;
}

function ResourcePage({resource,user}:{resource:Resource;user:Profile}) {
  const {data,loading,error,reload}=useRecords(resource);
  const [query,setQuery]=useState('');
  const [adding,setAdding]=useState(false);
  const rows=useMemo(()=>data.filter(item=>JSON.stringify(item).toLowerCase().includes(query.toLowerCase())),[data,query]);
  const ownsService=resource==='services' && data.some(item=>Number(item.profile)===Number(user.id));
  const canCreate=resource==='services' ? !ownsService : (resource==='properties'||resource==='bookings') && user.is_staff===true;

  async function deleteRecord(id:number|string) {
    if(!confirm('Delete this record? This action cannot be undone.'))return;
    try { await remove(resource,id);reload(); }
    catch(caught) { window.alert(errorMessage(caught)); }
  }

  return <section>
    <div className="page-head"><div><p className="eyebrow">Dwellora workspace</p><h1>{configs[resource].label}</h1><p className="muted">Connected to the Dwellora API.</p></div>{canCreate&&<button onClick={()=>setAdding(!adding)}>＋ Add {resource==='services'?'provider profile':'record'}</button>}</div>
    {resource==='services'&&ownsService&&<p className="inline-note">Your service-provider profile is already connected to this account.</p>}
    {adding&&<Editor resource={resource} onDone={()=>{setAdding(false);reload();}}/>}
    <div className="toolbar"><input aria-label="Search records" placeholder="Search records…" value={query} onChange={event=>setQuery(event.target.value)}/><button className="secondary" onClick={reload}>Refresh</button></div>
    {loading?<div className="empty">Loading records…</div>:error?<div className="empty error">{error}</div>:rows.length===0?<div className="empty">No records yet. New information will appear here.</div>:<div className="table-wrap"><table><thead><tr>{Object.keys(rows[0]).map(key=><th key={key}>{key.replaceAll('_',' ')}</th>)}<th>Actions</th></tr></thead><tbody>{rows.map((row,index)=>{
      const id=row.id;
      const mayDelete=id!=null&&((resource==='services'&&Number(row.profile)===Number(user.id))||((resource==='properties'||resource==='bookings')&&user.is_staff===true));
      return <tr key={String(id??index)}>{Object.keys(rows[0]).map(key=><td key={key}>{typeof row[key]==='object'?JSON.stringify(row[key]):String(row[key]??'—')}</td>)}<td>{mayDelete&&<button className="link danger" onClick={()=>deleteRecord(id as number|string)}>Delete</button>}</td></tr>;
    })}</tbody></table></div>}
  </section>;
}

export default function App() {
  const [user,setUser]=useState<Profile|null>(null);
  const [booting,setBooting]=useState(true);
  const [resource,setResource]=useState<Resource>('properties');

  async function loadProfile() {
    const profiles=await api.get<Profile[]>(endpoints.accounts.list);
    if(!profiles[0])throw new Error('Your account profile could not be loaded.');
    setUser(profiles[0]);
  }

  useEffect(()=>{
    const onExpired=()=>{setUser(null);setResource('properties');};
    window.addEventListener('dwellora:auth-expired',onExpired);
    if(!localStorage.getItem('dwellora_token'))setBooting(false);
    else loadProfile().catch(()=>{clearSession();setUser(null);}).finally(()=>setBooting(false));
    return ()=>window.removeEventListener('dwellora:auth-expired',onExpired);
  },[]);

  function signOut(){clearSession();setUser(null);setResource('properties');}
  async function authenticated(){await loadProfile();}

  if(booting)return <div className="boot-screen"><span className="brand-mark">DW</span><p>Connecting to Dwellora…</p></div>;
  if(!user)return <AuthScreen onAuthenticated={authenticated}/>;

  const visible=(Object.keys(configs) as Resource[]).filter(item=>item!=='bookings'||user.is_staff===true);
  return <>
    <aside><div className="brand"><span>DW</span><div>Dwellora<small>PROPERTY WORKSPACE</small></div></div><nav>{visible.map(item=><button className={resource===item?'active':''} onClick={()=>setResource(item)} key={item}>{configs[item].label}</button>)}</nav><div className="nav-note"><strong>{user.username}</strong><small>{user.email||'Dwellora member'}</small></div></aside>
    <main><header><div><span className="kicker">OPERATIONS</span><strong>Property workspace</strong></div><div className="header-user"><span>{user.is_staff?'Staff account':'Member account'}</span><button className="secondary" onClick={signOut}>Sign out</button></div></header><ResourcePage resource={resource} user={user}/></main>
  </>;
}
