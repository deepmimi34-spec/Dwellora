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

export type ListingStatus =
  | "draft"
  | "submitted"
  | "published"
  | "paused"
  | "rented"
  | "sold"
  | "expired"
  | "rejected"
  | "removed";

export interface ListingCharge extends ApiRecord {
  charge_type?: string;
  amount?: number | string | null;
  currency?: string;
  payer?: "tenant" | "buyer" | "lister" | "owner" | "shared" | "not_specified";
  frequency?: "one_time" | "monthly" | "yearly" | "other";
  is_required?: boolean | null;
  description?: string;
  source_note?: string;
}

export interface Listing extends ApiRecord {
  property?: Id;
  property_title?: string;
  lister?: Id;
  authorization?: Id | null;
  offer_type?: "rent" | "sale" | "short_stay";
  headline?: string;
  description?: string;
  unit_label?: string;
  price?: number | string;
  currency?: string;
  billing_period?: "total" | "night" | "month" | "year";
  advance_months?: number | null;
  costs_disclosed?: boolean;
  estimated_upfront_total?: number | string | null;
  availability_freshness?: "fresh" | "stale" | "not_confirmed";
  availability_confirmed_at?: string | null;
  available_from?: string | null;
  expires_at?: string | null;
  status?: ListingStatus;
  charges?: ListingCharge[];
}

export interface OwnershipClaim extends ApiRecord {
  property?: Id;
  claimant?: Id;
  ownership_type?: string;
  evidence_type?: string;
  status?: "claimed" | "under_review" | "verified" | "rejected" | "revoked";
  submitted_at?: string;
  reviewed_at?: string | null;
}

export interface ListingAuthorizationRecord extends ApiRecord {
  property?: Id;
  ownership?: Id;
  lister?: Id;
  authority_type?: "owner" | "agent" | "manager";
  status?: "requested" | "approved" | "rejected" | "revoked";
  valid_from?: string | null;
  valid_until?: string | null;
}

export interface ProductFeedback extends ApiRecord {
  category?: "bug" | "feature" | "usability" | "accessibility" | "data_quality" | "other";
  title?: string;
  description?: string;
  page_context?: string;
  device_context?: string;
  allow_public_idea?: boolean;
  status?: "received" | "triaged" | "planned" | "in_progress" | "shipped" | "declined";
  resolution_summary?: string;
  created_at?: string;
}
