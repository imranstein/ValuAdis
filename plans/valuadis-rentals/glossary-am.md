# Amharic (am) Glossary — ValuAdis Rentals

Machine-drafted Amharic — native-speaker review pending.

Purpose: keep terminology identical across the Nuxt web app (`frontend/app/locales/am.json`)
and the Flutter mobile app (`mobile-rentals/lib/l10n/app_am.arb`). Any new in-scope string that
uses one of these concepts must reuse the Amharic term below rather than inventing a new one.

Grounded in Proclamation No. 1320/2024 (የቤት ኪራይ ቁጥጥር አዋጅ ቁጥር 1320/2024) and the Addis Ababa
11.5% annual rent-increase cap it establishes.

| English term | Amharic | Notes |
|---|---|---|
| Rent | ኪራይ | Also root of "rental", "rented" |
| Rental / Rentals (product area) | ኪራይ | e.g. "Rentals" nav → "ኪራይ" |
| Contract | ውል | Tenancy contract = የኪራይ ውል |
| Tenancy contract | የኪራይ ውል | |
| Band / rent band | የኪራይ ክልል | "range" sense — the suggested min–max band |
| Suggested rent | የተጠቆመ ኪራይ | |
| Published (listing status) | የታተመ | past participle, matches "ታትሟል" for "has been published" |
| Under review (listing/application status) | በግምገማ ላይ | |
| Rented (listing status) | ተከራይቷል | "has been rented" |
| Withdrawn (listing status) | ተነስቷል | "has been withdrawn" |
| Deposit | ማስያዣ | security deposit |
| Application (rental application) | ማመልከቻ | |
| Apply (verb) | ማመልከት | |
| Applicant | አመልካች | |
| Verified owner | የተረጋገጠ ባለቤት | |
| Owner (property owner) | ባለቤት | |
| Renter / tenant | ተከራይ | |
| Officer (rental officer) | የኪራይ ኦፊሰር | |
| Listing (a published property-for-rent record) | ማስታወቂያ | |
| Sub-city | ክፍለ ከተማ | standard Addis Ababa administrative term |
| Proclamation 1320/2024 | አዋጅ ቁጥር 1320/2024 | full: የቤት ኪራይ ቁጥጥር አዋጅ ቁጥር 1320/2024 |
| Approved | ጸድቋል | |
| Rejected | ውድቅ ሆኗል | |
| Pending | በመጠባበቅ ላይ | |
| Sign up / Register | ይመዝገቡ | |
| Sign in / Log in | ይግቡ | |
| Sign out / Log out | ውጣ | |
| Profile | መገለጫ | |
| Fayda ID | ፋይዳ መታወቂያ | national digital ID |
| Rent index | የኪራይ መረጃ ጠቋሚ | market rent index |
| Language | ቋንቋ | |

## Conventions

- Prices always keep Western (Arabic) digits and the `ETB` currency code — do not localize
  numerals or the currency symbol (Ethiopian market convention).
- Dates stay Gregorian in v1 (Ethiopian calendar is noted as future work, not built here).
- Contract PDFs stay English pending legal direction — do not translate PDF generation.
