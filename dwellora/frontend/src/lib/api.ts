import { API_BASE_URL } from './endpoints';

export class ApiError extends Error {
  constructor(public status:number,message:string,public details?:unknown) {
    super(message);
    this.name='ApiError';
  }
}

function messageFor(status:number) {
  return ({
    400:'The server rejected the submitted fields.',
    401:'Your session has expired. Please sign in again.',
    403:'You do not have permission for this action.',
    404:'The requested resource was not found.',
    409:'This conflicts with an existing record.',
    422:'Some fields could not be processed.',
    500:'The server encountered an error.',
  } as Record<number,string>)[status] || 'The request could not be completed.';
}

export function clearSession() {
  localStorage.removeItem('dwellora_token');
  localStorage.removeItem('dwellora_refresh');
}

async function decode(response:Response):Promise<unknown> {
  const body=await response.text();
  if(!body)return null;
  try{return JSON.parse(body);}catch{return body;}
}

async function send(path:string,options:RequestInit,token?:string):Promise<Response> {
  const headers=new Headers(options.headers);
  if(options.body&&!headers.has('Content-Type'))headers.set('Content-Type','application/json');
  if(token)headers.set('Authorization','Bearer '+token);
  return fetch(API_BASE_URL+path,{...options,headers,credentials:'include'});
}

export async function request<T>(path:string,options:RequestInit={}):Promise<T> {
  const started=performance.now();
  let token=localStorage.getItem('dwellora_token')||undefined;
  try {
    let response=await send(path,options,token);
    if(response.status===401&&token&&!path.startsWith('/auth/token/')) {
      const refreshToken=localStorage.getItem('dwellora_refresh');
      if(refreshToken) {
        const refreshResponse=await fetch(API_BASE_URL+'/auth/token/refresh/',{
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body:JSON.stringify({refresh:refreshToken}),
        });
        const refreshed=await decode(refreshResponse) as {access?:string}|null;
        if(refreshResponse.ok&&refreshed?.access) {
          token=refreshed.access;
          localStorage.setItem('dwellora_token',token);
          response=await send(path,options,token);
        } else {
          clearSession();
          window.dispatchEvent(new CustomEvent('dwellora:auth-expired'));
        }
      } else {
        clearSession();
        window.dispatchEvent(new CustomEvent('dwellora:auth-expired'));
      }
    }
    const data=await decode(response);
    window.dispatchEvent(new CustomEvent('dwellora:api',{detail:{ok:response.ok,ms:Math.round(performance.now()-started)}}));
    if(!response.ok)throw new ApiError(response.status,messageFor(response.status),data);
    return data as T;
  } catch(error) {
    if(error instanceof ApiError)throw error;
    window.dispatchEvent(new CustomEvent('dwellora:api',{detail:{ok:false,ms:Math.round(performance.now()-started)}}));
    throw new ApiError(0,'Cannot reach the Django API. Check VITE_API_BASE_URL and CORS settings.');
  }
}

export const api = {
  get:<T>(path:string)=>request<T>(path),
  post:<T>(path:string,body:unknown)=>request<T>(path,{method:'POST',body:JSON.stringify(body)}),
  put:<T>(path:string,body:unknown)=>request<T>(path,{method:'PUT',body:JSON.stringify(body)}),
  patch:<T>(path:string,body:unknown)=>request<T>(path,{method:'PATCH',body:JSON.stringify(body)}),
  delete:<T>(path:string)=>request<T>(path,{method:'DELETE'}),
};
