import { api } from './api';
import { endpoints } from './endpoints';
import type { ApiRecord, Id } from '../types/api';

export const unwrap = (data: unknown): ApiRecord[] => Array.isArray(data) ? data as ApiRecord[] : (data && typeof data === 'object' && Array.isArray((data as {results?: unknown}).results) ? (data as {results: ApiRecord[]}).results : data ? [data as ApiRecord] : []);
export const list = (resource: keyof typeof endpoints) => api.get<unknown>((endpoints[resource] as {list: string}).list).then(unwrap);
export const create = (resource: keyof typeof endpoints, body: ApiRecord) => api.post<unknown>((endpoints[resource] as {create: string}).create, body);
export const update = (resource: keyof typeof endpoints, id: Id, body: ApiRecord) => api.put<unknown>((endpoints[resource] as {update: (id: Id) => string}).update(id), body);
export const remove = (resource: keyof typeof endpoints, id: Id) => api.delete<unknown>((endpoints[resource] as {remove: (id: Id) => string}).remove(id));
