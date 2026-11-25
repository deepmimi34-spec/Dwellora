import { api } from './api';
import { endpoints, type ApiRecord, type EndpointGroup, type Id } from './endpoints';

type EndpointValue = string | ((id: Id) => string);

function resolveEndpoint(value: EndpointValue | undefined, resource: EndpointGroup, action: string, id?: Id): string {
  if (!value) {
    throw new Error(`The ${action} operation is not configured for ${resource}.`);
  }
  return typeof value === 'function'
    ? (id === undefined ? (() => { throw new Error(`An ID is required for ${resource}.`); })() : value(id))
    : value;
}

function recordsFromResponse(payload: unknown): ApiRecord[] {
  if (Array.isArray(payload)) return payload as ApiRecord[];

  if (payload && typeof payload === 'object' && 'results' in payload) {
    const results = (payload as { results?: unknown }).results;
    if (Array.isArray(results)) return results as ApiRecord[];
  }

  throw new Error('The API returned an unexpected list response.');
}

export async function list(resource: EndpointGroup): Promise<ApiRecord[]> {
  const payload = await api.get<unknown>(endpoints[resource].list);
  return recordsFromResponse(payload);
}

export async function create(resource: EndpointGroup, data: ApiRecord): Promise<ApiRecord> {
  const path = resolveEndpoint(endpoints[resource].create, resource, 'create');
  return api.post<ApiRecord>(path, data);
}

export async function update(resource: EndpointGroup, id: Id, data: ApiRecord): Promise<ApiRecord> {
  const group = endpoints[resource] as { update?: EndpointValue };
  const path = resolveEndpoint(group.update, resource, 'update', id);
  return api.patch<ApiRecord>(path, data);
}

export async function remove(resource: EndpointGroup, id: Id): Promise<void> {
  const group = endpoints[resource] as { remove?: EndpointValue };
  const path = resolveEndpoint(group.remove, resource, 'delete', id);
  await api.delete<unknown>(path);
}
