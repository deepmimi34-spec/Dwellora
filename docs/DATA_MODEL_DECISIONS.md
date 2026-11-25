# Dwellora Core Data Model Decisions

**Status:** Proposed architecture for review before schema migrations  
**Scope:** Property ownership, listings, verification, reviews, comments and product feedback

## 1. Why the current model needs a boundary

The current `Property` model represents a property and also acts like a publishable listing. It has location and amenity fields, but it does not record who owns it, who is authorised to list it, its offer price, availability history or the interaction that would qualify someone to review it.

Those concepts should not be collapsed into a single table. A physical property may have several units and may be listed for rent, sale or short stay at different times. A landlord may authorise an agent to advertise it. A user may view a listing without ever becoming a tenant. A tenant may discover maintenance issues only after moving in.

The schema should represent those differences explicitly before public comments and reviews are released.

## 2. Proposed domain entities

### User and agency

- **Profile:** the authenticated person. A user may be a renter/buyer, owner, agent, developer or more than one of these. Do not rely on a single hard-coded role if a person can act in several capacities.
- **Agency:** a registered business or brokerage, if the platform needs multi-agent organisations.
- **AgencyMembership:** links a profile to an agency with a role and an active/inactive membership status.

The current `Profile` model can remain the user identity base. Role/agency work is a future schema change and must be designed with existing users in mind.

### Property and listing

- **Property:** the physical place or asset: address/area, property type and durable characteristics such as amenities. Keep owner/authority information separate from the public description.
- **PropertyUnit:** a rentable/sellable room, flat, apartment or unit within a property/building where applicable.
- **Listing:** a time-bound offer for rent, sale or short stay. It links to a property or unit, records the lister, records the authority basis for listing, has a lifecycle and can expire without deleting the underlying property.
- **ListingCost:** structured charges for the offer. Record rent/sale amount, currency, billing period, advance period, agency commission, viewing fee, deposit, service charges and who pays each charge. Unknown values remain unknown; never convert missing information to zero.
- **ListingAvailabilityEvent:** append-only history of availability confirmations and changes. Store who confirmed the state, when and by which channel.

**Important distinction:** `listed_by` is the person publishing and managing the listing; it does not prove that person owns the property. A landlord or lawful representative's authority should have its own review status and evidence trail.

### Trust and verification

Use separate verification records for separate claims:

1. Identity evidence for a person.
2. REAC licence evidence for an agent/broker or agency, with licence number, check date, result and link/reference to the public registry.
3. Authority-to-list evidence for the specific property/listing.
4. Property visit evidence, with inspector, date and scope of inspection.
5. Availability confirmation, with the date and confirming user.

A verification record should include status, reviewed_by, reviewed_at, expiry/recheck date, reason and a private evidence reference. Never expose identity documents or private evidence publicly. A property visit does not prove legal title, structural safety or absence of disputes. A REAC licence check does not prove an agent's behaviour or ownership of a particular property.

### Property interactions and reviews

- **PropertyInteraction:** records a user's meaningful interaction with a listing/property: viewing requested, viewing completed, tenancy started, tenancy ended or purchase completed. State transitions must be auditable. A booking or viewing record should identify the user and the exact listing/unit.
- **InteractionEvidence:** optional evidence reference and moderation state used to establish whether a review can be marked as verified. Keep sensitive documents private and minimise what is collected.
- **PropertyReview:** a review authored by a user and linked to the exact interaction that qualifies it. Enforce one review per eligible interaction. Record category ratings, overall rating, narrative, created_at and moderation state.
- **ReviewReply:** a listing manager/owner response to a review. Preserve the original review and any reply history; do not let a lister silently edit or remove a review.
- **ReviewReport:** a report for abuse, private information, threats, spam, conflict of interest or content unrelated to the experience.

A person who only viewed the place may leave feedback about the viewing and listing accuracy. Only a person with a verified tenancy/short-stay interaction should be allowed to rate lived-in aspects such as repairs, maintenance and landlord responsiveness. A sale review should require a verified transaction interaction before it is labelled as a completed purchase experience.

### Questions, comments and product feedback

Keep public property discussion separate from experience reviews:

- **ListingDiscussion:** a question or comment attached to a listing, with optional parent comment for replies. It is for pre-viewing questions and practical clarifications—not an endorsement or review.
- **DiscussionReport:** report spam, abusive content, private data or misleading claims. Listers may respond to questions only through an authorised account linked to that listing.
- **ProductFeedback:** feedback about Dwellora itself: bug, usability issue, accessibility issue, content concern or feature suggestion. Include a title, description, page/context, submitter where signed in, optional contact permission, moderation/triage status and timestamps.
- **ProductFeedbackUpdate:** status and response history so users can see whether feedback is received, being reviewed, planned, shipped or not planned.

Do not collect device identifiers, location or diagnostic details unless needed, explained and disclosed. Screenshots should be optional and warn users not to include private documents or sensitive details.

## 3. Review integrity and moderation rules

- Reviews must come from a recorded eligible interaction; no purchased reviews, seeded testimonials or fabricated ratings.
- Do not let a lister create a review for their own listing or use employee/agency accounts to simulate independent feedback.
- Label the interaction type clearly: `Verified viewing`, `Verified tenancy`, `Verified short stay` or `Verified transaction`.
- Allow users to report a review and submit an appeal if their content is moderated.
- Moderate threats, doxxing, hate, spam, irrelevant content and claims that expose private information. Preserve legitimate negative experience reports.
- Give the reviewed lister a right of reply, but never allow the reply to overwrite the review.
- Show the date and category ratings. Do not imply that star ratings verify legal ownership, title or building safety.
- Separate publicly visible information from private verification evidence and internal moderation notes.

## 4. Suggested implementation sequence

1. Confirm whether the existing production database has data and what tables currently exist.
2. Reconcile current apps/models and establish the custom user model's initial migration strategy.
3. Decide whether `Property` needs a safe backfill for existing records and introduce ownership/authority without breaking legacy entries.
4. Introduce Listing and structured cost/availability records with a data-preserving migration plan.
5. Introduce viewing/booking interactions and the eligibility rules.
6. Add ListingDiscussion for questions and lister replies with reporting and moderation.
7. Add PropertyReview only once eligible interactions can be verified.
8. Add ProductFeedback and the internal triage workflow.
9. Enable the consumer-facing endpoints and pages only after permission tests and migration checks pass.

## 5. Migration and deployment safeguards

Until an explicit owner/lister relationship is implemented and backfilled safely, property update and delete endpoints must remain staff-only. Ordinary authenticated users must not be allowed to change or remove listings belonging to other people. This is a temporary safety boundary, not the final landlord/agent workflow.

- Do not run `makemigrations` or `migrate` against production until current database tables, row counts and backups are inspected.
- For existing property rows, add new relationships as nullable first, preserve legacy records, and create an explicit reviewed backfill process. Do not infer that a user owns a legacy listing because they happen to be an administrator or creator in an unrelated record.
- Generate and inspect migrations in a development copy, run migration tests against a copy of the current database, and test rollback/restore procedures.
- Keep the custom user model stable. It must be established in the first migration for its app.
- Verify all create/update/delete querysets are scoped to the authenticated owner or authorised agency member.
- Add tests for cross-user access, invalid interaction state transitions, review duplication, review eligibility, comment abuse reports and private evidence visibility.

## 6. Release acceptance criteria

The review and comments feature is not ready until:

- A user cannot review a property without a qualifying interaction record.
- A visitor's review cannot be presented as a tenant's lived experience.
- Listers cannot edit/delete users' legitimate reviews.
- Users can ask questions and receive replies from authorised listers.
- Users can report problematic comments/reviews and see a clear report confirmation.
- Moderators can hide/reinstate content with an audit reason.
- Personal contact details and verification evidence are never exposed in public API responses.
- Product feedback can be classified, prioritised and closed with a user-visible status update.


## 7.5. Current safe API boundary

The stabilization branch currently exposes a limited set of endpoints:
- Account registration, JWT token issuance/refresh, and self-only profile reading/updating/deletion.
- Public property list and detail reads. Property create/update/delete are staff-only because the Property model does not yet track an owner or authorised lister.
- Public service-provider directory. Creating a provider profile requires authentication, and the OneToOne profile relationship is assigned by the server. Updates/deletion are scoped to the authenticated provider.
- Booking list/create/update/delete are staff-only until the booking model records the customer. Date validation and unavailable-unit rejection are in place.

Other property-type API modules remain unmounted while their imports, model references and permissions are reconciled. The current property and service APIs are not a substitute for the future consumer-facing marketplace experience.
