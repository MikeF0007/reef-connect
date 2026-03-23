import apiClient from '../lib/apiClient';

// ---------------------------------------------------------------------------
// Types — mirror backend Pydantic schemas (snake_case)
// ---------------------------------------------------------------------------

export interface UserProfile {
  id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  bio: string | null;
  avatar_url: string | null;
  first_name: string | null;
  last_name: string | null;
  location: string | null;
  website_url: string | null;
  birth_date: string | null;
}

export interface UserProfileUpdate {
  bio?: string | null;
  avatar_url?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  location?: string | null;
  website_url?: string | null;
  birth_date?: string | null;
}

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/** GET /api/users/me/profile */
export async function getMyProfile(): Promise<UserProfile> {
  const { data } = await apiClient.get<UserProfile>('/api/users/me/profile');
  return data;
}

/** PATCH /api/users/me/profile */
export async function updateMyProfile(updates: UserProfileUpdate): Promise<UserProfile> {
  const { data } = await apiClient.patch<UserProfile>('/api/users/me/profile', updates);
  return data;
}
