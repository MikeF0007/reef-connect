# Project Requirements & Assumptions

The ReefConnect app serves as a dive log and a social media platform, where users can create profiles and upload and attach media to their feed

# Phase 0 — Foundations

## Functional Requirements (FR)

### Authentication & Identity

* FR‑0.1 The system shall allow users to register with an email and password.  
* FR‑0.2 The system shall authenticate users and issue a signed JSON Web Token (JWT).  
* FR‑0.3 The system shall require a valid JWT for all authenticated API requests.  
* FR‑0.4 The system shall allow users to log out by invalidating client‑side authentication tokens.

### User Profile

* FR‑0.5 The system shall create a user profile upon successful registration.  
* FR‑0.6 The system shall allow users to view and edit their own profile information.  
* FR‑0.7 The system shall display a public‑facing profile for each user.

### Navigation

* FR‑0.8 The system shall provide navigation to the user profile, dive log creation, and friend list.

## Non‑Functional Requirements (NFR)

### Security

* NFR‑0.1 The system shall securely hash and store user passwords.  
* NFR‑0.2 The system shall validate JWTs on every authenticated request.  
* NFR‑0.3 The system shall protect against common web vulnerabilities.

### Scalability

* NFR‑0.4 The system shall be stateless at the API layer to support horizontal scaling.

# Phase 1 — Core Value: Personal Dive Log

## Functional Requirements (FR)

### Dive Logs

* FR‑1.1 The system shall allow users to create, edit, and delete dive log entries.  
* FR‑1.2 The system shall store dive metadata including date/time, location, temperature, duration, depth, and notes.  
* FR‑1.3 The system shall display list and detailed views of dive logs.  
* FR‑1.4 The system shall support pagination and sorting of dive logs.

### Media Uploads

* FR‑1.5 The system shall allow users to upload media associated with a dive log.  
* FR‑1.6 The system shall allow users to manage uploaded media.  
* FR‑1.7 The system shall generate thumbnails or previews for uploaded media.  
* FR‑1.8 The system shall allow users to delete their uploaded media.

### Species Tagging

* FR‑1.9 The system shall maintain a canonical species catalog with unique identifiers.  
* FR‑1.10 The system shall allow users to tag species on media items using unique identifiers.  
* FR‑1.11 The system shall allow users to remove species tags.  
* FR-1.12 The system shall remove species tags automatically when associated media is removed.  
* FR‑1.13 The system shall prevent duplicate species entries in the species catalog.

### ScubaDex

* FR‑1.14 The system shall derive a user’s ScubaDex from species tags associated with the user’s media and/or dive logs.  
* FR‑1.15 The ScubaDex shall list unique species encountered by the user (undiscovered species will be greyed out).  
* FR‑1.16 The system shall link ScubaDex entries to associated media when species is selected.  
* FR‑1.17 The system shall not allow direct manual editing of ScubaDex entries.  
* FR‑1.18 The system shall invalidate and rederive ScubaDex when media or tags are removed or modified.  
* FR‑1.19 The system shall remove ScubaDex entries when no remaining evidence exist

### Stats

* FR‑1.20 The system shall derive aggregated statistics from dive logs, media, and species tags.  
* FR‑1.21 The system shall display a stats dashboard for each user.

## Non‑Functional Requirements (NFR)

### Performance

* NFR‑1.1 The system shall paginate all list‑based endpoints.  
* NFR‑1.2 The system shall avoid unbounded queries over user data.

### Reliability

* NFR‑1.3 The system shall handle partial failures (e.g., media upload failure without corrupting dive data).

### Media Handling

* NFR‑1.4 The system shall process media uploads asynchronously.  
* NFR‑1.5 The system shall isolate original media from derived assets.

### Data Integrity

* NFR‑1.6 The system shall enforce referential integrity between users, dives, media, and species.  
* NFR‑1.7 The system shall ensure derived data (ScubaDex, stats) remains consistent with source data.  
* NFR‑1.8 The system shall allow derived data (ScubaDex, stats) to be recomputed from source data if needed.  
* NFR‑1.9 The system shall enforce uniqueness constraints on species identifiers.  
* NFR‑1.10 The system shall prevent duplicate species discovery counts caused by repeated tagging.  
* NFR‑1.11 The system shall prevent orphaned species tags when media is deleted.

# Phase 2 — Social Graph & Visibility

## Functional Requirements (FR)

### Friends

* FR‑2.1 The system shall allow users to send friend requests.  
* FR‑2.2 The system shall allow users to accept or decline friend requests.  
* FR‑2.3 The system shall maintain a list of confirmed friends.

### Profile Viewing

* FR‑2.4 The system shall allow users to view friend profiles.  
* FR‑2.5 The system shall support read‑only shared profile links.

### Privacy

* FR‑2.6 The system shall allow users to configure visibility of dives, media, and stats.

## Non‑Functional Requirements (NFR)

### Access Control

* NFR‑2.1 The system shall enforce visibility rules consistently across all endpoints.  
* NFR‑2.2 The system shall prevent indirect inference of private data.

# Phase 3 — Feed & Engagement

## Functional Requirements (FR)

### Activity Feed

* FR‑3.1 The system shall display an activity feed for each user.  
* FR‑3.2 The feed shall include friend activities such as new dives or achievements.

### Engagement

* FR‑3.3 The system shall allow users to like feed items.  
* FR‑3.4 The system shall allow users to comment on feed items.

### Notifications

* FR‑3.5 The system shall notify users of relevant social interactions.  
* FR‑3.6 The system shall provide an in‑app notification view.

## Non‑Functional Requirements (NFR)

### Performance

* NFR‑3.1 The system shall load the activity feed within acceptable latency.  
* NFR‑3.2 The system shall limit feed size and support pagination.

### Consistency

* NFR‑3.3 The system shall prevent duplicate engagement actions.  
* NFR‑3.4 The system shall ensure engagement counts remain accurate.

# Cross‑Cutting Non‑Functional Requirements (All Phases)

* NFR‑X.1 The system shall validate and sanitize all user input.  
* NFR‑X.2 The system shall log application errors and significant events.  
* NFR‑X.3 The system shall provide health checks for operational monitoring.  
* NFR‑X.4 The system shall be maintainable and extensible without major refactoring.  
* NFR‑X.5 The system shall document major architectural decisions and tradeoffs.

# Optional Features — Leaderboards, Badges, & Integrations

Note: The following features are optional and may be implemented incrementally without impacting core functionality.

## Optional Functional Requirements (FR)

### Leaderboards

* FR‑O.1 The system shall support leaderboards based on user statistics.  
* FR‑O.2 The system shall allow leaderboards to be scoped to a user’s friends.  
* FR‑O.3 The system shall support leaderboards for the following metrics:  
  * total number of dives  
  * total unique species discovered (ScubaDex)  
  * deepest recorded dive  
  * total dive time  
* FR‑O.4 The system shall display leaderboard rankings and user positions.  
* FR‑O.5 The system shall update leaderboard rankings when underlying stats change.

### Badges & Achievements

* FR‑O.6 The system shall define a set of badges or achievements for milestone events.  
* FR‑O.7 The system shall award badges automatically when milestone conditions are met.  
* FR‑O.8 The system shall display earned badges on a user’s profile.Example milestone categories (non‑exhaustive):  
  * Number of dives completed  
  * Maximum depth achieved  
  * Number of species discovered in ScubaDex  
  * Number of media uploads  
  * Number of badges/achievements

### Certifications earned

* FR‑O.9 The system shall prevent duplicate awarding of the same badge.

### Auto Species Identification

* FR‑O.10 The system shall support automated species identification on uploaded media.  
* FR‑O.11 The system shall allow users to confirm or reject automated identifications.

### External Integrations

* FR‑O.12 The system shall support importing dive data from external providers (i.e. Garmin).  
* FR‑O.13 The system shall map external data into the internal dive log format.  
* FR‑O.14 The system shall prevent duplicate dive creation during repeated imports.

## Optional Non‑Functional Requirements (NFR)

### Performance & Scalability

* NFR‑O.1 The system shall compute leaderboard rankings efficiently.  
* NFR‑O.2 The system shall avoid recomputing leaderboard data synchronously on every request.  
* NFR‑O.3 The system shall allow leaderboard and badge computation to be performed asynchronously.

### Consistency & Integrity

* NFR‑O.4 The system shall ensure leaderboard rankings reflect accurate underlying statistics.  
* NFR‑O.5 The system shall ensure badge awards remain consistent with user data over time.

### External Dependency Handling

* NFR‑O.6 The system shall tolerate failures of optional external services without impacting core features.  
* NFR‑O.7 The system shall isolate optional feature logic from core domain logic.