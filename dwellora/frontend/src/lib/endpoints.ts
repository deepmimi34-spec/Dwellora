import type { ApiRecord, Id } from '../types/api';
export type { ApiRecord, Id };

const root = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/').replace(/\/$/, '');
export const API_BASE_URL = root;

/** API paths are kept in one place so backend route changes remain explicit. */
export const endpoints = {
  accounts: { create: '/accounts/profile/', list: '/accounts/profile/view_details/', update: '/accounts/profile/update/', remove: '/accounts/profile/delete/' },
  properties: { create: '/property/property/create/', list: '/property/property/list/', detail: (id: Id) => `/property/property/${id}/detail/`, update: (id: Id) => `/property/property/${id}/update/`, remove: (id: Id) => `/property/property/${id}/delete/` },
  bookings: { create: '/booking/hostel_booking/', list: '/booking/hostel_view/', update: '/booking/hostel_update/', remove: '/booking/hostel_delete/' },
  hostels: { create: '/hostels/create_bookings', list: '/hostels/list', detail: (id: Id) => `/hostels/detail/${id}/`, update: '/hostels/update_booking' },
  hotels: { create: '/hotels/hostel/create/', list: '/hotels/hostel/list/', detail: '/hotels/hostel/detail/', update: '/hotels/hostel/update/', remove: '/hotels/hostel/delete/' },
  services: { create: '/services/create_service/', list: '/services/create_service/', detail: (id: Id) => `/services/create_service/${id}/`, update: (id: Id) => `/services/update_service/${id}/`, remove: (id: Id) => `/services/delete_service/${id}/` }
} as const;

export type EndpointGroup = keyof typeof endpoints;
