import type { ApiRecord } from './api';
export interface Profile extends ApiRecord { username?: string; email?: string; bio?: string }
export interface Property extends ApiRecord { title?: string; property_type?: string; region?: string; city?: string; furnished?: boolean; parking?: boolean; water_available?: boolean; internet_available?: boolean; kitchen_available?: boolean }
export interface HostelUnit extends ApiRecord { name?: string }
export interface Booking extends ApiRecord { hostel?: number; start_date?: string; end_date?: string; created_at?: string }
