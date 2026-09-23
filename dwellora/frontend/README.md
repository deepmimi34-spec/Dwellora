# Dwellora Manager frontend

The React/Vite manager lives in this directory and leaves the Django backend untouched.

```bash
cd dwellora/frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` to the root URL that includes the Django API prefix (for example `http://127.0.0.1:8000/api/`). The client uses browser session cookies and also accepts an optional `dwellora_token` local-storage value as a Bearer token; the repository does not expose Django REST authentication settings, so no authentication scheme is assumed.

## Backend audit (from the available app URL/view files)

| Frontend module | Django app | Actual endpoint paths | Methods exposed by views | Connected? |
|---|---|---|---|---|
| Profiles | accounts | `/accounts/profile/`, `/accounts/profile/view_details/`, `/accounts/profile/update/`, `/accounts/profile/delete/` | POST, GET, PUT/PATCH, DELETE | Yes |
| Properties | property | `/property/property/create/`, `/property/property/<pk>/detail/`, `/property/property/<pk>/update/`, `/property/property/<pk>/delete/` | POST, GET (the detail view is declared `ListAPIView`), PUT/PATCH, DELETE | Partial: list endpoint is not declared in the supplied urls |
| Hostel units | hostels | `/hostels/create_bookings`, `/hostels/list`, `/hostels/detail/<pk>/`, `/hostels/update_booking` | POST, GET, GET, PUT/PATCH | Yes |
| Hotels | hotels | `/hotels/hostel/list/`, `/hotels/hostel/create/`, `/hotels/hostel/detail/`, `/hotels/hostel/update/`, `/hotels/hostel/delete/` | GET, POST, GET, PUT/PATCH, DELETE | Yes, subject to the backend's missing pk parameters |
| Bookings | booking | `/booking/hostel_booking/`, `/booking/hostel_view/`, `/booking/hostel_update/`, `/booking/hostel_delete/` | POST, GET, PUT/PATCH, DELETE | Yes |
| Services | services | `/services/create_service/`, `/services/create_service/<pk>/`, `/services/update_service/<pk>/`, `/services/delete_service/<pk>/` | POST, GET/PUT/PATCH, GET/PUT/PATCH, GET/PUT/PATCH (delete view is `RetrieveUpdateAPIView`, not DELETE) | Partial: deletion is intentionally not offered |
| Apartments, houses, rentals, locations, verification | supplied apps | No usable API URL/views/serializers were supplied | — | No; unsupported functionality is hidden |

Serializer-backed fields are intentionally not invented: properties use the model fields (`title`, `property_type`, `region`, `city`, and the five boolean amenities); profiles use `id`, `username`, `email`, write-only `password`, and `bio`; bookings use model fields; other forms remain minimal until their serializers expose fields. Django validation responses are surfaced in the add form.

Known backend limitations are documented rather than worked around: the root `urls.py`, settings/auth configuration, and several app serializers were not present in the repository tree, and some view/path definitions omit primary-key parameters or use a non-delete view for a delete-named route. Update endpoint wiring is retained only where the backend declares an update view.
