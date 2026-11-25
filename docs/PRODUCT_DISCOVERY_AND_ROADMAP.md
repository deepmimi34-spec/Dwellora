# Dwellora Product Discovery and Differentiation Plan

**Research reviewed:** 25 November 2026  
**Market focus:** Ghana, with a mobile-first experience for local and diaspora users  
**Product direction:** A trustworthy property discovery, viewing and decision-support platform—not merely another listing directory.

## 1. Executive direction

Dwellora should compete on the quality and trustworthiness of the property decision, not on the raw number of listings. The core product promise should be:

> Find a property, understand the full cost, know who is listing it, see what has actually been checked, arrange a viewing, and learn from people with real experience.

A polished search experience is necessary, but the differentiated value is a transparent evidence trail around each listing and a feedback loop that helps improve the marketplace over time.

## 2. Research findings

### Ghana market signals

1. **Viewing and agent charges need transparency.** Ghana News Agency documented tenant concerns about advance viewing/registration charges, transport costs and agent commissions. Graphic Online also reported complaints about viewing fees and visits to properties that were unavailable or did not match requirements. These are documented reports, not a measure of how frequently every agent behaves this way.
2. **Professional credentials should be checkable.** The Real Estate Agency Council (REAC) provides a public registry for licensed practitioners and agencies, information about disciplinary actions and a public complaints route. REAC's information on Act 1047 describes licensing obligations for real-estate practitioners.
3. **Identity checks must not be overstated.** meQasa explains that its agent verification checks identity documents and agency documents, while explicitly warning that its badge does not guarantee business conduct. Dwellora should be equally precise about what each badge means.
4. **Direct communication and easy viewings are becoming expected.** Ghana property apps describe direct contact, saved listings and scheduled viewings as important parts of the discovery journey. These are competitors' product claims, not independently verified service-quality results.

### International product patterns worth learning from

- **Airbnb:** Reviews are connected to completed stays; guests can rate distinct aspects such as cleanliness, accuracy, communication, location and value. Public host replies provide context. This is a useful model for authentic property feedback.
- **Rightmove:** Saved properties, saved searches, alerts and shared lists make a long property search easier to manage.
- **Ghana marketplace apps:** Plate and PMC advertise direct messaging, map-based discovery, viewing requests, price alerts and mobile-first property browsing. Dwellora should evaluate these patterns without copying their branding or assuming their claims are independently verified.

### Community feedback and app-store usability signals

These are qualitative comments and small app-store samples, not representative market research. They are useful for identifying problems to test with real Dwellora users.

- In a r/TechGhana discussion, a renter asked for a place where people could review a property before signing. The poster described problems that only became apparent after moving in; replies supported a broader service-review idea. This is a strong signal to distinguish **viewed the property** from **lived there** and to let verified residents describe maintenance and landlord communication.
- In r/ghana discussions, renters described properties that were already taken, changing prices, unreliable agents and continued reliance on WhatsApp or personal referrals. Treat these as individual experiences, but make availability freshness and enquiry reliability core product requirements.
- A public meQasa app review reproduced by an app-review aggregator reported that saved properties, sharing and the image-viewer close action did not work reliably. The sample is small, so this is a concrete usability test idea—not a conclusion about the whole service.
- PMC's App Store release notes describe useful operational patterns: in-app chat, report-a-problem follow-up, blocking/reporting conversations, accessible text/screen-reader support, map/list consistency and preventing duplicate viewing requests. Its listing showed only two ratings when reviewed, so do not infer broad satisfaction from the score.
- A Ghana housing community post proposed exact neighbourhoods, real GHS prices, actual-property photos/video and visible agency-fee information. Treat these as community design suggestions, not universal rules.

The resulting Dwellora acceptance tests should include: saved homes persist after signing out and back in; share links open the correct listing; closing a photo viewer returns users to the same search position and filters; duplicate viewing requests are blocked; map and list result counts agree; and the interface remains usable with large text and screen readers.

## 3. The Dwellora experience we should build

### A. A listing with a transparent cost breakdown

Every rental listing should be able to show, separately:

- Advertised monthly rent or total sale price.
- Required advance period in months.
- Rent payable upfront, calculated from rent and advance period.
- Agent commission, with amount or percentage and who pays it.
- Viewing or registration charge, including whether it is required and who receives it.
- Security deposit, service charge and other recurring or one-time fees.
- Estimated upfront move-in total, with a clear note that it is based on lister-provided figures.

Do not silently combine these into one price. Display unknown charges as **Not provided**, not GHS 0. A buyer or tenant should be able to compare the actual cost of two properties.

### B. Evidence-based trust labels

Use separate, explainable states rather than one generic verified badge:

- **Identity checked:** Dwellora checked the lister's submitted identity evidence.
- **REAC licence checked:** a licence number was checked against the official registry, with date and result recorded.
- **Property visit recorded:** a Dwellora-approved inspection recorded the location and date. This does not certify title or structural safety.
- **Availability confirmed:** the lister recently reconfirmed that the property is available.
- **Documents reviewed:** identify the kind of document reviewed and the limitations of that check.

Every label must explain who checked it, when it was checked and what it does not prove. Do not imply that Dwellora has verified land title unless there is a separate, qualified legal verification process.

### C. Listing freshness and accuracy

- Show **Last confirmed** date and the source of the confirmation.
- Ask listers to reconfirm availability on a regular schedule.
- Mark listings as unconfirmed when the deadline passes; do not keep presenting them as freshly available.
- Let users report unavailable, duplicate, misleading-price, inaccurate-photo or suspicious listings.
- Preserve a moderation/audit trail when a listing is edited, hidden or restored.

### D. Reviews, questions and comments

Keep three different forms of feedback separate:

1. **Property reviews:** structured ratings and written experience reports. Only users with a recorded, eligible viewing, booking or tenancy interaction can publish a verified-experience review. The UI must show which interaction qualifies.
2. **Property questions and comments:** public questions about a listing, with lister replies. Clearly distinguish answers from independent reviews. Require sign-in to post, provide report controls, rate-limit abuse and moderate before or after publication according to risk.
3. **Dwellora product feedback:** a separate feedback channel for bugs, confusing workflows, accessibility issues and feature requests. Collect an optional satisfaction score, page/context, device/browser information only where disclosed, and a user-written description. Allow users to track whether a suggestion is received, under review, planned, shipped or declined.

### E. Useful review categories

For rental experiences, consider:
- Listing accuracy and move-in condition
- Cleanliness and maintenance
- Landlord/agent communication and responsiveness to repairs
- Water, electricity and internet reliability (show as experience reports, not guaranteed infrastructure facts)
- Viewing and move-in process
- Location, access and noise
- Clarity of fees and value for money
- Overall experience

For short stays, use stay-specific categories such as cleanliness, check-in and communication. For a sale listing, do not reuse stay-related categories. Add transaction-specific categories only when Dwellora can verify the relevant interaction. Allow verified visitors to write about the viewing process, but reserve resident-only categories for a recorded tenancy interaction.

Reviews should have a visible date, an experience-verification label, moderation/report action and a right of reply. Do not allow listers to delete legitimate negative reviews. Provide an appeal/moderation workflow for abuse, private information, threats or demonstrably irrelevant content.

### F. Discovery and convenience

- Mobile-first search with Ghana regions, cities and neighbourhoods.
- Filters for rent/sale, property type, price, bedrooms, furnishings and amenities.
- Map and list views, with a clear location-privacy choice.
- Save properties and searches; alerts for new matches, price changes and availability changes.
- Compare shortlisted homes side by side.
- Schedule viewings and manage enquiries in one inbox.
- A low-data browsing mode: compressed images, clear loading states and no forced sign-in before basic discovery.

## 4. Recommended build order

### Foundation before feature expansion
1. Reconcile the owner/lister relationship and user roles.
2. Review custom-user authentication and password handling.
3. Define listing lifecycle, availability confirmation and audit history.
4. Define the money fields and how totals are calculated.
5. Resolve database-table naming and migration strategy without losing existing data.

### Release 1 — Trustworthy listings
- Lister ownership and permission boundaries.
- Cost breakdown and upfront-cost calculator.
- Availability confirmation timestamps and stale-listing handling.
- Listing reports and moderation queue.
- Explicit identity and REAC licence verification states.

### Release 2 — Search and viewing
- Consumer-facing property discovery pages.
- Better filters, map/list results, saved homes and alerts.
- Viewing requests and an enquiry inbox.
- Mobile and low-bandwidth usability.

### Release 3 — Community and feedback
- Public property Q&A/comments.
- Verified-interaction property reviews and lister replies.
- Abuse reporting, moderation, appeals and review integrity controls.
- Dwellora product feedback centre and public feature-status tracking.
- A simple, visible "Report a problem / Suggest an improvement" entry point with a confirmation and status update.

### Release 4 — Decision intelligence
- Comparable asking-price context where reliable data exists.
- Affordability and total-cost comparisons.
- Personalised recommendations that explain why a property matches.
- Carefully sourced area information. Clearly label estimates and external data.

## 5. Product metrics and learning loop

Track product usefulness, not just page views:

- Share of active listings with complete pricing and recent availability confirmation.
- Listing report rate and time to resolve reports.
- Search-to-enquiry and enquiry-to-viewing conversion.
- Viewing request completion and no-show rates.
- Review coverage for eligible completed interactions.
- Reported review abuse and moderation response time.
- Product feedback categories, upvotes, resolution time and repeat complaints.
- Mobile load time and API error rate.

Every month, group feedback by issue, user type and journey step. Prioritise repeated problems by user impact, frequency, trust/safety risk and implementation cost. Publish short release notes explaining what changed because of user feedback.

## 6. Product rules we should not compromise

- Never invent reviews, star ratings, verification badges or testimonials.
- Never label a listing or lister verified without recording exactly what was checked.
- Never make a review appear to come from a tenant or buyer unless the qualifying interaction is recorded.
- Never expose a reviewer's phone number, email, private message or identity document.
- Never accept payment or imply escrow protection until payment, dispute, compliance and refund workflows are properly designed.
- Never treat a high review score as proof of title, safety or legal ownership.
- Give users a straightforward way to report a problem and see what happens next.

## 7. Research sources

The source list below records the public material used for this product discovery. Competitor product pages and app-store descriptions are treated as claims about advertised features, not independent proof of quality.

### Ghana market and trust
- Ghana News Agency, tenant concerns about exploitative agents and landlords: https://gna.org.gh/2023/05/tenants-appeal-for-protection-from-exploitative-agents-and-landlords/
- Graphic Online, reports on charges and viewing-fee problems: https://www.graphic.com.gh/lifestyle/life/outrageous-charges-by-agents-take-toll-on-tenants.html
- Real Estate Agency Council public registry: https://reac.gov.gh/public-registry-search/
- REAC public services and complaints: https://reac.gov.gh/public-services/
- REAC licensing information: https://reac.gov.gh/licence/
- meQasa agent/agency verification FAQ: https://meqasa.com/faq
- Plate · Homes app description (advertised features): https://play.google.com/store/apps/details?id=gh.plate.app
- PMC app description, release notes and ratings: https://apps.apple.com/gh/app/pmc-real-estate-rentals/id6738896407
- Meqasa App Store listing and release history: https://apps.apple.com/gh/app/meqasa/id1401184947
- Meqasa user-review sample (third-party review aggregation; small sample): https://apprecs.com/android/com.meqasa.search2/meqasa
- Reddit r/TechGhana, request for a property-review platform: https://www.reddit.com/r/TechGhana/comments/1tqa4ca/app_or_website_to_review_a_property_before_renting/
- Reddit r/ghana, house-hunting and stale-listing experiences: https://www.reddit.com/r/ghana/comments/1qck7dg/for_expatsdiaspora_what_do_you_wish_you_knew/
- Reddit r/ghana, current discussion about finding rentals and avoiding scams: https://www.reddit.com/r/ghana/comments/1wukf70/renting_in_ghana/
- Reddit r/ghana, community discussion of rental search pain points: https://www.reddit.com/r/ghana/comments/1trl3o1/how_are_people_actually_finding_houses_in_ghana/

### International patterns
- Airbnb, why reviews matter: https://www.airbnb.com/resources/hosting-homes/a/why-reviews-matter-41
- Airbnb, safety tips for choosing a place and reading reviews: https://www.airbnb.com/help/article/241
- Rightmove, account features: https://faq.rightmove.co.uk/support/solutions/articles/7000048780-what-can-i-do-with-a-myrightmove-account/

## 8. Implementation note

This document is the product direction and acceptance baseline, not a claim that every feature is already implemented.

**Now enabled in the stabilization branch:**
- JWT account registration, token issue/refresh and authenticated profile access.
- Public property listing and detail reads.
- Staff-only property creation, editing and deletion until owner/lister relationships are modelled.
- Public service-provider directory; authenticated provider-profile creation; owner-scoped provider-profile update and deletion.
- Staff-only booking management until booking ownership is represented, with date and unit-availability validation.
- Responsive sign-in/register screens and a workspace limited to currently mounted API resources.

**Implemented and tested, but not yet publicly released:**
- Property interaction records for viewing, tenancy, short stay and purchase.
- Member-owned interaction requests; staff-only completion and verification.
- Reviews tied to one completed, staff-verified interaction, with one review per interaction and category ratings.
- Property questions/comments with member moderation queue and official staff responses.
- Reporting for abusive, misleading, spam or privacy-violating reviews/comments; users see their own reports and staff can record a resolution.
- Separate feedback URL configuration so these features can be mounted only after database migrations are reviewed and applied.

The latest completed CI run discovered **60 backend tests and all 60 passed**, including interaction ownership, verification, review eligibility, comment moderation and content reporting. Frontend production build and Django checks also passed. These tests validate the code, not a production migration.

**Still planned:** transparent full-cost listing breakdowns, listing freshness/confirmation history, owner-authorised lister replies, a dedicated Dwellora product-feedback centre, appeals and a public marketplace experience. Reviews/comments remain unavailable from the active API because their model migrations have not been generated/applied. The current Property model also lacks a verified owner/lister relationship. No production migrations have been generated or applied. Before exposing these routes, inspect the deployed database, take a backup and prepare a data-preserving migration plan.
