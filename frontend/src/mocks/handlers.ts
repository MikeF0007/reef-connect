import { http, HttpResponse } from 'msw';
import { User } from '../app/types';
import type { UserProfile, UserProfileUpdate } from '../api/userApi';
import type {
  UserCertification,
  UserCertificationCreate,
  UserCertificationUpdate,
} from '../api/certificationApi';

// ---------------------------------------------------------------------------
// Mock credential store — mirrors initializeDemoData.ts
// ---------------------------------------------------------------------------
interface MockCredential {
  password: string;
  user: User;
}

const MOCK_CREDENTIALS: Record<string, MockCredential> = {
  'demo@reefconnect.com': {
    password: 'demo',
    user: {
      id: 'demo-user-1',
      email: 'demo@reefconnect.com',
      username: 'DemoUser',
      bio: 'Passionate scuba diver exploring the oceans',
      certifications: ['PADI Open Water', 'PADI Advanced'],
      createdAt: new Date('2024-01-01').toISOString(),
      privacySettings: {
        profileVisibility: 'public',
        diveLogsVisibility: 'public',
        mediaVisibility: 'public',
        statsVisibility: 'public',
      },
    },
  },
  'sarah@example.com': {
    password: 'password',
    user: {
      id: 'demo-user-2',
      email: 'sarah@example.com',
      username: 'SarahDiver',
      bio: 'Marine biologist and dive instructor',
      certifications: ['PADI Divemaster', 'SSI Instructor'],
      createdAt: new Date('2024-02-15').toISOString(),
      privacySettings: {
        profileVisibility: 'public',
        diveLogsVisibility: 'public',
        mediaVisibility: 'public',
        statsVisibility: 'public',
      },
    },
  },
  'mike@example.com': {
    password: 'password',
    user: {
      id: 'demo-user-3',
      email: 'mike@example.com',
      username: 'MikeOcean',
      bio: 'Technical diver and underwater photographer',
      certifications: ['TDI Technical Diver', 'PADI Rescue Diver'],
      createdAt: new Date('2024-03-10').toISOString(),
      privacySettings: {
        profileVisibility: 'public',
        diveLogsVisibility: 'public',
        mediaVisibility: 'public',
        statsVisibility: 'public',
      },
    },
  },
};

// ---------------------------------------------------------------------------
// In-memory profile store — keyed by user ID, seeded from mock credentials
// ---------------------------------------------------------------------------
const MOCK_PROFILES: Record<string, UserProfile> = {
  'demo-user-1': {
    id: 'profile-1',
    user_id: 'demo-user-1',
    created_at: new Date('2024-01-01').toISOString(),
    updated_at: new Date('2024-01-01').toISOString(),
    bio: 'Passionate scuba diver exploring the oceans',
    avatar_url: null,
    first_name: 'Demo',
    last_name: 'User',
    location: null,
    website_url: null,
    birth_date: null,
  },
  'demo-user-2': {
    id: 'profile-2',
    user_id: 'demo-user-2',
    created_at: new Date('2024-02-15').toISOString(),
    updated_at: new Date('2024-02-15').toISOString(),
    bio: 'Marine biologist and dive instructor',
    avatar_url: null,
    first_name: 'Sarah',
    last_name: null,
    location: null,
    website_url: null,
    birth_date: null,
  },
  'demo-user-3': {
    id: 'profile-3',
    user_id: 'demo-user-3',
    created_at: new Date('2024-03-10').toISOString(),
    updated_at: new Date('2024-03-10').toISOString(),
    bio: 'Technical diver and underwater photographer',
    avatar_url: null,
    first_name: 'Mike',
    last_name: null,
    location: null,
    website_url: null,
    birth_date: null,
  },
};

// ---------------------------------------------------------------------------
// In-memory certification store — keyed by user ID, seeded from mock credentials
// ---------------------------------------------------------------------------
let certIdCounter = 7;

function makeCert(
  id: string,
  userId: string,
  name: string,
  issuer: string,
  issuedDate: string,
  expiryDate: string | null = null,
): UserCertification {
  return {
    id,
    user_id: userId,
    created_at: new Date('2024-01-01').toISOString(),
    updated_at: new Date('2024-01-01').toISOString(),
    certification_name: name,
    issuer,
    issued_date: issuedDate,
    expiry_date: expiryDate,
    certification_number: null,
    notes: null,
    verified: null,
  };
}

const MOCK_CERTIFICATIONS: Record<string, UserCertification[]> = {
  'demo-user-1': [
    makeCert('cert-1', 'demo-user-1', 'PADI Open Water Diver', 'PADI', '2022-06-15'),
    makeCert('cert-2', 'demo-user-1', 'PADI Advanced Open Water', 'PADI', '2022-09-20'),
  ],
  'demo-user-2': [
    makeCert('cert-3', 'demo-user-2', 'PADI Divemaster', 'PADI', '2021-03-10'),
    makeCert('cert-4', 'demo-user-2', 'SSI Instructor', 'SSI', '2020-11-05'),
  ],
  'demo-user-3': [
    makeCert('cert-5', 'demo-user-3', 'TDI Technical Diver', 'TDI', '2023-01-20'),
    makeCert('cert-6', 'demo-user-3', 'PADI Rescue Diver', 'PADI', '2021-07-30'),
  ],
};

/** Extract user ID from the mock JWT written at login. */
function getUserIdFromRequest(request: Request): string | null {
  const auth = request.headers.get('Authorization');
  if (!auth) return null;
  // Format: "Bearer mock-jwt.<userId>.<timestamp>"
  const token = auth.replace('Bearer ', '');
  const parts = token.split('.');
  return parts.length >= 2 ? parts[1] : null;
}

// ---------------------------------------------------------------------------
// Handlers
// ---------------------------------------------------------------------------
export const handlers = [
  // POST /api/auth/login
  http.post('http://localhost:8000/api/auth/login', async ({ request }) => {
    try {
      const body = await request.json() as { email: string; password: string };
      const credential = MOCK_CREDENTIALS[body.email];

      if (!credential || credential.password !== body.password) {
        return HttpResponse.json(
          { error: 'Invalid email or password', code: 'UNAUTHORIZED' },
          { status: 401 },
        );
      }

      // Mock JWT: not a real signed token — swap for real in Phase 4b
      const mockToken = `mock-jwt.${credential.user.id}.${Date.now()}`;

      return HttpResponse.json({ user: credential.user, token: mockToken });
    } catch (error) {
      return HttpResponse.json(
        { error: 'Server error', code: 'INTERNAL_ERROR' },
        { status: 500 },
      );
    }
  }),

  // POST /api/auth/register — stub (Phase 4b)
  http.post('/api/auth/register', () => {
    return HttpResponse.json(
      { error: 'Register not yet implemented in mock', code: 'NOT_IMPLEMENTED' },
      { status: 501 },
    );
  }),

  // GET /api/auth/me — stub (Phase 4b)
  http.get('/api/auth/me', () => {
    return HttpResponse.json(
      { error: '/me not yet implemented in mock', code: 'NOT_IMPLEMENTED' },
      { status: 501 },
    );
  }),

  // POST /api/auth/logout — stub (Phase 4b)
  http.post('/api/auth/logout', () => {
    return HttpResponse.json({ success: true });
  }),

  // GET /api/users/me/profile
  http.get('http://localhost:8000/api/users/me/profile', ({ request }) => {
    const userId = getUserIdFromRequest(request);
    if (!userId) {
      return HttpResponse.json({ error: 'Unauthorized', code: 'UNAUTHORIZED' }, { status: 401 });
    }
    const profile = MOCK_PROFILES[userId];
    if (!profile) {
      return HttpResponse.json({ error: 'Profile not found', code: 'NOT_FOUND' }, { status: 404 });
    }
    return HttpResponse.json(profile);
  }),

  // PATCH /api/users/me/profile
  http.patch('http://localhost:8000/api/users/me/profile', async ({ request }) => {
    const userId = getUserIdFromRequest(request);
    if (!userId) {
      return HttpResponse.json({ error: 'Unauthorized', code: 'UNAUTHORIZED' }, { status: 401 });
    }
    const existing = MOCK_PROFILES[userId];
    if (!existing) {
      return HttpResponse.json({ error: 'Profile not found', code: 'NOT_FOUND' }, { status: 404 });
    }
    const body = await request.json() as UserProfileUpdate;
    const updated: UserProfile = {
      ...existing,
      ...body,
      updated_at: new Date().toISOString(),
    };
    MOCK_PROFILES[userId] = updated;
    return HttpResponse.json(updated);
  }),

  // GET /api/users/me/certifications
  http.get('http://localhost:8000/api/users/me/certifications', ({ request }) => {
    const userId = getUserIdFromRequest(request);
    if (!userId) {
      return HttpResponse.json({ error: 'Unauthorized', code: 'UNAUTHORIZED' }, { status: 401 });
    }
    return HttpResponse.json(MOCK_CERTIFICATIONS[userId] ?? []);
  }),

  // POST /api/users/me/certifications
  http.post('http://localhost:8000/api/users/me/certifications', async ({ request }) => {
    const userId = getUserIdFromRequest(request);
    if (!userId) {
      return HttpResponse.json({ error: 'Unauthorized', code: 'UNAUTHORIZED' }, { status: 401 });
    }
    const body = await request.json() as UserCertificationCreate;
    const cert: UserCertification = {
      id: `cert-${certIdCounter++}`,
      user_id: userId,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      certification_name: body.certification_name,
      issuer: body.issuer,
      issued_date: body.issued_date,
      expiry_date: body.expiry_date ?? null,
      certification_number: body.certification_number ?? null,
      notes: body.notes ?? null,
      verified: body.verified ?? null,
    };
    if (!MOCK_CERTIFICATIONS[userId]) {
      MOCK_CERTIFICATIONS[userId] = [];
    }
    MOCK_CERTIFICATIONS[userId].push(cert);
    return HttpResponse.json(cert, { status: 201 });
  }),

  // PATCH /api/users/me/certifications/:certificationId
  http.patch(
    'http://localhost:8000/api/users/me/certifications/:certificationId',
    async ({ request, params }) => {
      const userId = getUserIdFromRequest(request);
      if (!userId) {
        return HttpResponse.json({ error: 'Unauthorized', code: 'UNAUTHORIZED' }, { status: 401 });
      }
      const list = MOCK_CERTIFICATIONS[userId] ?? [];
      const idx = list.findIndex((c) => c.id === params.certificationId);
      if (idx === -1) {
        return HttpResponse.json({ error: 'Certification not found', code: 'NOT_FOUND' }, { status: 404 });
      }
      const body = await request.json() as UserCertificationUpdate;
      const patch = Object.fromEntries(
        Object.entries(body as Record<string, unknown>).filter(([, v]) => v != null),
      );
      const updated: UserCertification = { ...list[idx], ...patch, updated_at: new Date().toISOString() };
      list[idx] = updated;
      return HttpResponse.json(updated);
    },
  ),

  // DELETE /api/users/me/certifications/:certificationId
  http.delete(
    'http://localhost:8000/api/users/me/certifications/:certificationId',
    ({ request, params }) => {
      const userId = getUserIdFromRequest(request);
      if (!userId) {
        return HttpResponse.json({ error: 'Unauthorized', code: 'UNAUTHORIZED' }, { status: 401 });
      }
      const list = MOCK_CERTIFICATIONS[userId] ?? [];
      const idx = list.findIndex((c) => c.id === params.certificationId);
      if (idx === -1) {
        return HttpResponse.json({ error: 'Certification not found', code: 'NOT_FOUND' }, { status: 404 });
      }
      list.splice(idx, 1);
      return new HttpResponse(null, { status: 204 });
    },
  ),

  // GET /api/users/:userId/certifications
  http.get('http://localhost:8000/api/users/:userId/certifications', ({ params }) => {
    return HttpResponse.json(MOCK_CERTIFICATIONS[params.userId as string] ?? []);
  }),
];
