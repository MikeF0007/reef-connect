import { http, HttpResponse } from 'msw';
import { User } from '../app/types';

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
];
