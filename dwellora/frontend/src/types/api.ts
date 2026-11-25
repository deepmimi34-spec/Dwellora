export type Id = number | string;
export type ApiRecord = Record<string, unknown> & { id?: Id };

export interface Profile extends ApiRecord {
  username?: string;
  email?: string;
  bio?: string;
  is_staff?: boolean;
}

export interface Property extends ApiRecord {
  title?: string;
  property_type?: string;
  region?: string;
  city?: string;
  furnished?: boolean;
  parking?: boolean;
  water_available?: boolean;
  internet_available?: boolean;
  kitchen_available?: boolean;
}

export interface HostelUnit extends ApiRecord {
  name?: string;
  unit_name?: string;
}

export interface Booking extends ApiRecord {
  hostel?: number;
  start_date?: string;
  end_date?: string;
  created_at?: string;
}
