import { useMemo, useState } from 'react';
import { create, remove } from './lib/services';
import { endpoints } from './lib/endpoints';
import { useRecords } from './hooks/useRecords';
import type { ApiRecord } from './types/api';

const configs = {
  properties: { label: 'Properties', fields: ['title', 'property_type', 'region', 'city', 'furnished', 'parking', 'water_available', 'internet_available', 'kitchen_available'] },
  hostels: { label: 'Hostel units', fields: ['name'] },
  bookings: { label: 'Bookings', fields: ['hostel', 'start_date', 'end_date'] },
  hotels: { label: 'Hotels', fields: [] },
  services: { label: 'Services', fields: [] },
  accounts: { label: 'Profiles', fields: ['username', 'email', 'password', 'bio'] },
} as const;
type Resource = keyof typeof configs;

function Editor({ resource, onDone }: { resource: Resource; onDone: () => void }) {
  const fields = configs[resource].fields;
  const [form, setForm] = useState<ApiRecord>({});
  const [error, setError] = useState('');
  return <form className="editor" onSubmit={e => {
    e.preventDefault();
    create(resource, form).then(onDone).catch(x => setError(x.details ? JSON.stringify(x.details) : x.message));
  }}>
    <h3>Add {configs[resource].label.slice(0, -1)}</h3>
    {fields.map(f => <label key={f}>{f}<input type={f.includes('date') ? 'date' : f === 'password' ? 'password' : 'text'} onChange={e => setForm({ ...form, [f]: e.target.value })} /></label>)}
    {error && <p className="error">{error}</p>}
    <button>Save</button>
  </form>;
}

function ResourcePage({ resource }: { resource: Resource }) {
  const { data, loading, error, reload } = useRecords(resource);
  const [query, setQuery] = useState('');
  const [adding, setAdding] = useState(false);
  const rows = useMemo(() => data.filter(x => JSON.stringify(x).toLowerCase().includes(query.toLowerCase())), [data, query]);
  return <section>
    <div className="page-head"><div><p className="eyebrow">Dwellora Manager</p><h1>{configs[resource].label}</h1><p className="muted">Live data from the Django REST API.</p></div>{'create' in endpoints[resource] && <button onClick={() => setAdding(!adding)}>＋ Add</button>}</div>
    {adding && <Editor resource={resource} onDone={() => { setAdding(false); reload(); }} />}
    <div className="toolbar"><input placeholder="Search returned records…" value={query} onChange={e => setQuery(e.target.value)} /><button className="secondary" onClick={reload}>Refresh</button></div>
    {loading ? <div className="empty">Loading records…</div> : error ? <div className="empty error">{error}</div> : rows.length === 0 ? <div className="empty">No records returned.</div> : <div className="table-wrap"><table><thead><tr>{Object.keys(rows[0]).map(k => <th key={k}>{k}</th>)}<th>Actions</th></tr></thead><tbody>{rows.map((row, i) => {
      const recordId = row.id;
      return <tr key={String(recordId ?? i)}>{Object.keys(rows[0]).map(k => <td key={k}>{typeof row[k] === 'object' ? JSON.stringify(row[k]) : String(row[k] ?? '—')}</td>)}<td>{recordId != null && 'remove' in endpoints[resource] && <button className="link danger" onClick={() => { if (confirm('Delete this record?')) remove(resource, recordId).then(reload).catch(() => {}); }}>Delete</button>}</td></tr>;
    })}</tbody></table></div>}
  </section>;
}

export default function App() {
  const [resource, setResource] = useState<Resource>('properties');
  return <><aside><div className="brand"><span>DW</span><div>Dwellora<small>Manager</small></div></div><nav>{(Object.keys(configs) as Resource[]).map(r => <button className={resource === r ? 'active' : ''} onClick={() => setResource(r)} key={r}>{configs[r].label}</button>)}</nav><div className="nav-note">Backend-first console<br /><small>No unsupported actions are shown.</small></div></aside><main><header><div><span className="kicker">OPERATIONS</span><strong>Property workspace</strong></div><span className="kicker">MANAGER</span></header><ResourcePage resource={resource} /></main></>;
}
