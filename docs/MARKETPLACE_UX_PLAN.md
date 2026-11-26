# Dwellora Marketplace UX Blueprint

## Design direction
Trust-first Ghana property marketplace. The visual system should be clean, modern, calm and mobile-first. Prioritise the user's decision-making over decoration: price clarity, property photos, location, availability recency, verified authority scope and direct next actions.

## Consumer discovery
- Search by city/area, property type, rent/sale/short-stay and price.
- Filter by bedrooms/bathrooms, amenities, furnished, availability date, advance period and disclosed costs.
- Map/list toggle; map pins represent individual Listings, not physical Property rows.
- Sort by relevance, newest, price, and recently confirmed availability.
- Listing cards must show: price/billing period, unit, location, property type, cost-disclosure status, availability-confirmed date, verification scope and save action.
- A stale or incomplete listing is never disguised as current or fully costed.

## Ghana-specific trust signals (separate, never one generic badge)

1. **Account identity** — Dwellora account identity check (scope and date shown).
2. **REAC practitioner licence** — manual registry check until a supported registry API is available; show licence category/number masked, current status and checked date, with link to the official register. This is not ownership proof. A current staff-verified REAC licence is required for agent/manager authorization approval.
3. **Property ownership claim** — Dwellora staff review of submitted evidence; clearly say “Ownership claim reviewed by Dwellora”, not “legal title guaranteed”.
4. **Listing authority** — owner or authorised lister for this specific property, checked and dated.
5. **Availability** — lister-confirmed date; stale after 30 days and excluded from active search.
6. **Verified experience** — review only after completed, staff-verified interaction.
7. **Content moderation** — report action and visible moderation outcome where appropriate.

These signals remain independent. A REAC-licensed agent may still have no authority for a particular property; a verified ownership claim is not a structural inspection or title guarantee.

## Listing detail
Information hierarchy:
1. Gallery with accessible keyboard/swipe controls and photo count.
2. Headline, location, offer type, base price and billing period.
3. Trust block: ownership/agent-authority status with exact scope, availability last-confirmed date and listing freshness.
4. Upfront breakdown: advance, deposit, agent fee, viewing fee, service charge, other one-time charges, payer, mandatory/optional/unknown. Missing values display “Not provided”; never zero by default.
5. Property facts and amenities, unit details, location map.
6. Questions/comments and published verified-experience reviews, with category score breakdown.
7. Report content action and listing feedback.
8. Viewing request CTA. Do not collect a viewing fee through Dwellora until payment rules and refund/anti-fraud controls are separately designed.

## Viewing and review trust
- A viewing request has a status and user-visible timeline.
- Review eligibility is based on completed, staff-verified interaction, not self-assertion.
- Reviewer identity may be displayed as a privacy-safe profile label; never expose email/phone by default.
- Reviews include category ratings and text, pending moderation state for the author, published state for public.
- Questions/comments and reviews are separate; property lister replies must be authorised by the ownership/listing authority.

## Lister workspace
- Onboarding progress: account → property → ownership claim/evidence → listing authority (if agent) → offer details → costs → availability confirmation → review/publish.
- Draft autosave, clear validation and step navigation.
- Lister can see staff review status and a reason/request for additional evidence.
- Cost disclosure checklist blocks submission until all upfront/recurring charges are entered or explicitly marked unknown/not applicable.
- Availability confirmation history and automatic “reconfirm” prompt when 30 days old.
- Listings status dashboard: Draft, Submitted, Published, Paused, Rented/Sold, Rejected, Expired.

## Product feedback
- Persistent contextual “Give feedback” action on app pages.
- Category, title, detail, optional route-only context and optional device context (user supplied).
- No automatic device fingerprint, full URL query string, account contact info or sensitive telemetry.
- Private submissions by default; show acknowledgement and a user's feedback history.
- Feedback status labels and anonymised resolution summary; internal staff notes never visible to submitter.
- Staff prioritisation should aggregate themes, frequency and impact. A single severe accessibility/security/data-integrity issue must not be buried by popularity voting.

## Responsive and accessibility requirements
- Mobile: one-column property results, bottom action bar on detail, touch-sized controls, filter sheet and map toggle.
- Desktop: split discovery layout and persistent filter rail; property detail with gallery/content plus anchored viewing action.
- Keyboard accessible gallery, filters, map/list switch, save, forms and dialogs.
- Visible focus, semantic labels, WCAG AA contrast, reduced-motion support.
- Loading skeletons, empty search suggestions, network errors, stale availability and unverified authority all get explicit states.

## Release sequence
1. Run database audit and migration rehearsal; enable listing API routes in staging.
2. Lister workflow and staff review UI.
3. Consumer search/list/detail and saved listings.
4. Viewing request journey and notifications.
5. Review/comments/report UI.
6. Contextual product feedback and triage dashboard.
7. Pilot, usability testing, measure search-to-viewing conversion, stale-listing rate, cost disclosure completion, report resolution time and repeat usage.

## External research references

- REAC official public registry: https://reac.gov.gh/public-registry-search/ (registry for licensed practitioners and disciplinary actions)
- REAC licensing/verification information: https://reac.gov.gh/licence/
- meQasa FAQs: https://meqasa.com/faq (favourites/saved properties and advertiser features)
- NestGhana Help: https://nestghana.com/help (competitor-described agent verification, owner confirmation, reporting and fee policies)
- FieRent Terms: https://fierent.com/terms (states its marketplace does not confirm ownership or agent identity)
