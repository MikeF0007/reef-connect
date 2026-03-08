# ReefConnect API Requirements

## Design Principles

- Bundle related data to minimize round trips
- Use pagination for list endpoints (default: 20 items, max: 100)
- Return nested objects where appropriate to avoid N+1 queries
- Use consistent response structures

---

## 1. Authentication & User Management

### `POST /api/auth/register`

**Purpose:** Create new user account

**Request Body:**

```typescript
{
  email: string;
  username: string;
  password: string;
}
```

**Response:**

```typescript
{
  user: User; // includes id, email, username, bio, avatar, createdAt, privacySettings
  token: string; // JWT
}
```

---

### `POST /api/auth/login`

**Purpose:** Authenticate existing user

**Request Body:**

```typescript
{
  email: string;
  password: string;
}
```

**Response:**

```typescript
{
  user: User;
  token: string;
}
```

---

### `POST /api/auth/logout`

**Purpose:** Invalidate session (server-side if needed)

**Response:**

```typescript
{
  success: boolean;
}
```

---

### `GET /api/auth/me`

**Purpose:** Get current authenticated user (validates token)

**Response:** `User`

---

## 2. User Profiles

### `GET /api/users/:user_id/profile`

**Purpose:** Get user profile with privacy-aware data bundling

**Query Parameters:**

- `include?: string[]` - Optional: `['stats', 'badges', 'recentDives']`

**Response:**

```typescript
{
  id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  bio?: string;
  avatar_url?: string;
  first_name?: string;
  last_name?: string;
  location?: string;
  website_url?: string;
  birth_date?: string;
}
```

---

### `PATCH /api/users/me/profile`

**Purpose:** Update current user's profile

**Request Body:**

```typescript
{
  bio?: string;
  avatar_url?: string;
  first_name?: string;
  last_name?: string;
  location?: string;
  website_url?: string;
  birth_date?: string; // ISO date string
}
```

**Response:** `User`

---

### `PATCH /api/users/me/privacy`

**Purpose:** Update privacy settings (bundled in one call)

**Request Body:**

```typescript
{
  profileVisibility?: 'public' | 'private' | 'unlisted';
  diveLogsVisibility?: 'public'| 'private' | 'unlisted';
  mediaVisibility?: 'public' | 'private' | 'unlisted';
  statsVisibility?: 'public' | 'private' | 'unlisted';
}
```

**Response:** `PrivacySettings`

---

### `GET /api/users/me/profile`

**Purpose:** Get current user's own profile (full data including private fields)

**Response:** `UserProfile`

---

### `GET /api/users/me/settings`

**Purpose:** Get current user's settings

**Response:** `UserSettings`

---

### `PATCH /api/users/me/settings`

**Purpose:** Update current user's settings

**Request Body:**

```typescript
{
  preferred_units?: 'metric' | 'imperial';
  timezone?: string;
  language?: string;
}
```

**Response:** `UserSettings`

---

### `GET /api/users/me/privacy`

**Purpose:** Get current user's privacy settings

**Response:** `PrivacySettings`

---

### `GET /api/users/:user_id/certifications`

**Purpose:** Get user's certifications (subject to profile privacy settings)

**Response:** `UserCertification[]` (empty array if profile is private or not visible)

---

### `POST /api/users/me/certifications`

**Purpose:** Add a new certification

**Request Body:**

```typescript
{
  certification_name: string;
  issuer: string;
  issued_date: string; // ISO date string
  expiry_date?: string; // ISO date string
  certification_number?: string;
  notes?: string;
  verified?: boolean;
}
```

**Response:** `UserCertification`

---

### `PATCH /api/users/me/certifications/:certification_id`

**Purpose:** Update a certification

**Request Body:**

```typescript
{
  certification_name?: string;
  issuer?: string;
  issued_date?: string;
  expiry_date?: string;
  certification_number?: string;
  notes?: string;
  verified?: boolean;
}
```

**Response:** `UserCertification`

---

### `DELETE /api/users/me/certifications/:certification_id`

**Purpose:** Delete a certification

**Response:** `204 No Content`

---

## 3. Dive Logs

### `GET /api/divelogs`

**Purpose:** Get dive logs for a user

**Query Parameters:**

- `user_id?: string` (defaults to current user)
- `sort_by?: 'date' | 'max_depth' | 'duration' | 'location' | 'experience_rating'` (default: 'date')
- `order?: 'asc' | 'desc'` (default: 'desc')
- `limit?: number` (1-100, default: 20)
- `offset?: number` (default: 0)

**Response:** `DiveLog[]`

---

### `GET /api/divelogs/date-range`

**Purpose:** Get dive logs within a date range for a user

**Query Parameters:**

- `user_id?: string` (defaults to current user)
- `start_date: string` (YYYY-MM-DD)
- `end_date: string` (YYYY-MM-DD)
- `sort_by?: 'date' | 'max_depth' | 'duration' | 'location' | 'experience_rating'` (default: 'date')
- `order?: 'asc' | 'desc'` (default: 'desc')
- `limit?: number` (1-100, default: 20)
- `offset?: number` (default: 0)

**Response:** `DiveLog[]`

---

### `GET /api/divelogs/location/{location}`

**Purpose:** Get dive logs by location (partial match on dive site) for a user

**Query Parameters:**

- `user_id?: string` (defaults to current user)
- `sort_by?: 'date' | 'max_depth' | 'duration' | 'location' | 'experience_rating'` (default: 'date')
- `order?: 'asc' | 'desc'` (default: 'desc')
- `limit?: number` (1-100, default: 20)
- `offset?: number` (default: 0)

**Response:** `DiveLog[]`

---

### `GET /api/divelogs/:dive_log_id`

**Purpose:** Get detailed dive log

**Response:** `DiveLog`

---

### `POST /api/divelogs`

**Purpose:** Create new dive log

**Request Body:**

```typescript
{
  // Required fields
  date: string;
  title: string;
  site: string;
  duration: number;
  max_depth: number;
  log_visibility: 'public' | 'private' | 'unlisted';

  // Dive Basics (optional)
  period?: 'morning' | 'afternoon' | 'night';
  start_type?: 'boat' | 'shore';
  type?: 'reef' | 'wall' | 'drift' | 'cave' | 'deep' | 'shipwreck' | 'other';
  purpose?: 'recreational' | 'training' | 'research' | 'restoration' | 'other';

  // Measurements (optional)
  avg_depth?: number;
  visibility_description?: string;
  location?: {
    lat: number;
    long: number;
  };

  // Environmental (optional)
  weather?: 'sunny' | 'partly cloudy' | 'cloudy' | 'rainy' | 'windy' | 'foggy';
  air_temp?: number;
  surface_temp?: number;
  bottom_temp?: number;
  water_type?: 'salt' | 'fresh' | 'brackish';
  body_of_water?: 'ocean' | 'lake' | 'river' | 'quarry' | 'cenote';
  wave?: 'none' | 'small' | 'medium' | 'large';
  current?: 'none' | 'light' | 'moderate' | 'strong';
  surge?: 'none' | 'light' | 'moderate' | 'strong';

  // Equipment (optional JSONB fields)
  equipment?: any;
  gas_mix?: any;
  cylinder_pressure?: any;
  safety_stops?: any;

  // People/Experience (optional)
  buddy?: string;
  dive_center?: string;
  experience_feeling?: 'amazing' | 'good' | 'average' | 'poor';
  experience_rating?: number;
  public_notes?: string;
  private_notes?: string;
}
```

**Response:** `DiveLog`

---

### `PATCH /api/divelogs/:dive_log_id`

**Purpose:** Update existing dive log

**Request Body:** All fields from POST are optional for updates

**Response:** `DiveLog`

---

### `DELETE /api/divelogs/:dive_log_id`

**Purpose:** Delete dive log

**Response:**

```typescript
{
  message: string;
}
```

---

## 4. Media

### `POST /api/media/upload`

**Purpose:** Upload media to a dive log

**Request Body:** `FormData` with:

- `file: File`
- `dive_log_id: string`
- `caption?: string`

**Response:**

```typescript
{
  media: Media; // includes thumbnailUrl when available
  uploadStatus: 'accepted' | 'rejected'; // validation feedback - was upload accepted?
}
```

---

### `DELETE /api/media/:media_id`

**Purpose:** Delete media (removes associated tags automatically)

**Response:**

```typescript
{
  success: boolean;
  removedTagsCount: number;
}
```

---

### `PATCH /api/media/:media_id`

**Purpose:** Update media description

**Request Body:**

```typescript
{
  description?: string;
}
```

**Response:** `Media`

---

### `GET /api/media`

**Purpose:** Get media for user or dive log, including associated species tags

**Query Parameters:**

- `user_id?: string`
- `dive_log_id?: string`
- `media_type?: string`
- `limit?: number` (1-100, default: 20)
- `offset?: number` (default: 0)

**Response:** Array<{
media: Media;
tags: Array<{
tag: SpeciesTag;
species: Species;
}>;
}>

---

## 5. Species Tagging

### `POST /api/media/:media_id/tags`

**Purpose:** Tag a species on media

**Request Body:**

```typescript
{
  species_id: string;
}
```

**Response:**

```typescript
{
  tag: SpeciesTag;
  species: Species;
}
```

---

### `DELETE /api/media/:media_id/tags/:tag_id`

**Purpose:** Remove species tag

**Response:**

```typescript
{
  success: boolean;
}
```

---

### `GET /api/species`

**Purpose:** Get species catalog for tagging

**Query Parameters:**

- `search?: string`
- `category?: string`
- `limit?: number` (1-100, default: 20)
- `offset?: number` (default: 0)

**Response:** Species[]

---

## 6. ScubaDex

### `GET /api/scubadex/:user_id`

**Purpose:** Get user's ScubaDex (discovered species)

**Query Parameters:**

- `include_media?: boolean` (include sample media for each species)

**Response:**

```typescript
{
  entries: Array<{
    species: Species;
    first_seen_date: string;
    encounter_count: number;
    sample_media?: Media[]; // max 3 if includeMedia=true
  }>;
  total_discovered: number;
  total_species: number; // in catalog
  percent_complete: number;
}
```

---

## Additional Information

### Batch Initialization Endpoint

Consider a batch endpoint for initial app load to reduce round trips:

```typescript
 ### 'GET /api/init'

Response: {
  user: User;
  stats: UserStats;
  unreadNotifications: number;
  pendingFriendRequests: number;
}
```

### Pagination Standards

All paginated endpoints should follow this pattern:

**Query Parameters:**

- `limit?: number` (1-100, default: 20)
- `offset?: number` (default: 0)

**Response Structure:** `T[]`

### Error Response Format

Standardize all error responses:

```typescript
{
  error: string;          // Human-readable message
  code: string;           // Machine-readable code (e.g., "UNAUTHORIZED")
  details?: any;          // Optional additional context
  timestamp: string;      // ISO timestamp
}
```

**Common Error Codes:**

- `UNAUTHORIZED` - Missing or invalid authentication
- `FORBIDDEN` - Insufficient permissions
- `NOT_FOUND` - Resource doesn't exist
- `VALIDATION_ERROR` - Invalid request data
- `CONFLICT` - Resource conflict (e.g., duplicate friend request)
- `RATE_LIMIT_EXCEEDED` - Too many requests

### Rate Limiting

Document rate limits in response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
```

### Authentication

All endpoints except `/api/auth/register` and `/api/auth/login` require:

**Header:**

```
Authorization: Bearer <JWT_TOKEN>
```
