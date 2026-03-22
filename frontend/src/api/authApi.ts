import apiClient from '../lib/apiClient';
import { User } from '../app/types';

export interface AuthResponse {
  user: User;
  token: string;
}

/**
 * POST /api/auth/login
 * Authenticates an existing user and returns a JWT + user object.
 */
export async function loginUser(email: string, password: string): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>('/api/auth/login', { email, password });
  return data;
}

// Stubs — will be wired to real endpoints in Phase 4b

/** POST /api/auth/register */
export async function registerUser(
  email: string,
  password: string,
  username: string,
): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>('/api/auth/register', {
    email,
    password,
    username,
  });
  return data;
}

/** GET /api/auth/me */
export async function getMe(): Promise<User> {
  const { data } = await apiClient.get<User>('/api/auth/me');
  return data;
}

/** POST /api/auth/logout */
export async function logoutUser(): Promise<void> {
  await apiClient.post('/api/auth/logout');
}
