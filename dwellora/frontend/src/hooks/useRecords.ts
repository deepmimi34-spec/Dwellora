import { useEffect, useState } from 'react';
import { ApiError } from '../lib/api';
import { list } from '../lib/services';
import type { ApiRecord } from '../types/api';
export function useRecords(resource: Parameters<typeof list>[0]) { const [data,setData]=useState<ApiRecord[]>([]); const [loading,setLoading]=useState(true); const [error,setError]=useState(''); const reload=()=>{setLoading(true);setError('');list(resource).then(setData).catch((e: ApiError)=>setError(e.message)).finally(()=>setLoading(false));}; useEffect(reload, [resource]); return {data,loading,error,reload}; }
