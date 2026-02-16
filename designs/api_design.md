# ReefConnect API Requirements

## Design Principles

- Bundle related data to minimize round trips
- Use pagination for list endpoints (default: 20 items, max: 100)
- Return nested objects where appropriate to avoid N+1 queries
- Include metadata (counts, has_more flags) for better UX
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

### `GET /api/users/:userId/profile`

**Purpose:** Get user profile with privacy-aware data bundling

**Query Parameters:**

- `include?: string[]` - Optional: `['stats', 'badges', 'recentDives']`

**Response:**

```typescript
{
  user: User; // email only included if viewing own profile
  stats?: UserStats; // if included and visible
  badges?: Badge[]; // if included
  friendshipStatus?: 'none' | 'pending_sent' | 'pending_received' | 'friends';
  isOwnProfile: boolean;
}
```

---

### `PATCH /api/users/me/profile`

**Purpose:** Update current user's profile

**Request Body:**

```typescript
{
  username?: string;
  bio?: string;
  avatar?: string;
}
```

**Response:** `User`

---

### `PATCH /api/users/me/privacy`

**Purpose:** Update privacy settings (bundled in one call)

**Request Body:**

```typescript
{
  profileVisibility?: 'public' | 'private';
  diveLogsVisibility?: 'public'| 'private';
  mediaVisibility?: 'public' | 'private';
  statsVisibility?: 'public' | 'private';
}
```

**Response:** `PrivacySettings`

---

### `GET /api/users/:userId/certifications`

**Purpose:** Get user's certifications (subject to profile privacy settings)

**Response:** `UserCertification[]` (empty array if profile is private or not visible)

---

### `POST /api/users/me/certifications`

**Purpose:** Add a new certification

**Request Body:**

```typescript
{
  certificationName: string;
  issuer: string;
  issuedDate: string; // ISO date string
  expiryDate?: string; // ISO date string
  certificationNumber?: string;
  notes?: string;
}
```

**Response:** `UserCertification`

---

### `PATCH /api/users/me/certifications/:certificationId`

**Purpose:** Update a certification

**Request Body:**

```typescript
{
  certificationName?: string;
  issuer?: string;
  issuedDate?: string;
  expiryDate?: string;
  certificationNumber?: string;
  notes?: string;
  verified?: boolean;
}
```

**Response:** `UserCertification`

---

### `DELETE /api/users/me/certifications/:certificationId`

**Purpose:** Delete a certification

**Response:** `204 No Content`

---

## 3. Dive Logs

### `GET /api/divelogs`

**Purpose:** Get paginated dive logs for a user

**Query Parameters:**

- `userId?: string` (defaults to current user)
- `page?: number`
- `limit?: number`
- `sortBy?: 'date' | 'maxDepth' | 'duration' | 'location' | 'experienceRating'` (default: 'date')
- `order?: 'asc' | 'desc'` (default: 'desc')

**Response:**

```typescript
{
  diveLogs: DiveLog[];
  total: number;
  page: number;
  hasMore: boolean;
}
```

---

### `GET /api/divelogs/:diveLogId`

**Purpose:** Get detailed dive log with associated media

**Response:**

```typescript
{
  diveLog: DiveLog;
  media: Array<{
    media: Media;
    tags: Array<{
      tag: SpeciesTag;
      species: Species;
    }>;
  }>; // NOTE: If dive logs frequently have >50 media items, consider adding pagination with query params: ?mediaPage=1&mediaLimit=20
  canEdit: boolean; // permission check
}
```

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
  maxDepth: number;
  visibility: 'public' | 'private' | 'unlisted';

  // Dive Basics (optional)
  period?: 'morning' | 'afternoon' | 'night';
  startType?: 'boat' | 'shore';
  type?: 'reef' | 'wall' | 'drift' | 'cave' | 'deep' | 'shipwreck' | 'other';
  purpose?: 'recreational' | 'training' | 'research' | 'restoration' | 'other';

  // Measurements (optional)
  avgDepth?: number;
  visibilityDescription?: string;
  location?: {
    lat: number;
    lng: number;
  };

  // Environmental (optional)
  weather?: 'sunny' | 'partly cloudy' | 'cloudy' | 'rainy' | 'windy' | 'foggy';
  airTemp?: number;
  surfaceTemp?: number;
  bottomTemp?: number;
  waterType?: 'salt' | 'fresh' | 'brackish';
  bodyOfWater?: 'ocean' | 'lake' | 'river' | 'quarry' | 'cenote';
  wave?: 'none' | 'small' | 'medium' | 'large';
  current?: 'none' | 'light' | 'moderate' | 'strong';
  surge?: 'none' | 'light' | 'moderate' | 'strong';

  // Equipment (optional JSONB fields)
  equipment?: any;
  gasMix?: any;
  cylinderPressure?: any;
  safetyStops?: any;

  // People/Experience (optional)
  buddy?: string;
  diveCenter?: string;
  experienceFeeling?: 'amazing' | 'good' | 'average' | 'poor';
  experienceRating?: number;
  publicNotes?: string;
  privateNotes?: string;

  // Meta (optional)
  metadata?: any;
}
```

**Response:** `DiveLog`

---

### `PATCH /api/divelogs/:diveLogId`

**Purpose:** Update existing dive log

**Request Body:** All fields from POST are optional for updates

**Response:** `DiveLog`

---

### `DELETE /api/divelogs/:diveLogId`

**Purpose:** Delete dive log and associated media

**Response:**

```typescript
{
  success: boolean;
  deletedMediaCount: number;
}
```

---

## 4. Media

### `POST /api/media/upload`

**Purpose:** Upload media to a dive log

**Request Body:** `FormData` with:

- `file: File`
- `diveLogId: string`
- `caption?: string`

**Response:**

```typescript
{
  media: Media; // includes thumbnailUrl when available
  uploadStatus: 'accepted' | 'rejected'; // validation feedback - was upload accepted?
}
```

---

### `DELETE /api/media/:mediaId`

**Purpose:** Delete media (removes associated tags automatically)

**Response:**

```typescript
{
  success: boolean;
  removedTagsCount: number;
}
```

---

### `PATCH /api/media/:mediaId`

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

- `userId?: string`
- `diveLogId?: string`
- `mediaType?: string`
- `page?: number`
- `limit?: number`

**Response:**

```typescript
{
  media: Array<{
    media: Media;
    tags: Array<{
      tag: SpeciesTag;
      species: Species;
    }>;
  }>;
  total: number;
  hasMore: boolean;
}
```

---

## 5. Species Tagging

### `POST /api/media/:mediaId/tags`

**Purpose:** Tag a species on media

**Request Body:**

```typescript
{
  speciesId: string;
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

### `DELETE /api/media/:mediaId/tags/:tagId`

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
- `page?: number`
- `limit?: number`

**Response:**

```typescript
{
  species: Species[];
  total: number;
  hasMore: boolean;
}
```

---

## 6. ScubaDex

### `GET /api/scubadex/:userId`

**Purpose:** Get user's ScubaDex (discovered species)

**Query Parameters:**

- `includeMedia?: boolean` (include sample media for each species)

**Response:**

```typescript
{
  entries: Array<{
    species: Species;
    firstSeenDate: string;
    encounterCount: number;
    sampleMedia?: Media[]; // max 3 if includeMedia=true
  }>;
  totalDiscovered: number;
  totalSpecies: number; // in catalog
  percentComplete: number;
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

- `page?: number` (default: 1)
- `limit?: number` (default: 20, max: 100)

**Response Structure:**

```typescript
{
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasMore: boolean;
  };
}
```

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
