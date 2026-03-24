import apiClient from '../lib/apiClient';

// ---------------------------------------------------------------------------
// Types — mirror backend Pydantic schemas (snake_case)
// ---------------------------------------------------------------------------

export interface UserCertification {
  id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  certification_name: string;
  issuer: string;
  issued_date: string;       // ISO date string (YYYY-MM-DD)
  expiry_date: string | null;
  certification_number: string | null;
  notes: string | null;
  verified: boolean | null;
}

export interface UserCertificationCreate {
  certification_name: string;
  issuer: string;
  issued_date: string;       // ISO date string (YYYY-MM-DD)
  expiry_date?: string | null;
  certification_number?: string | null;
  notes?: string | null;
  verified?: boolean | null;
}

export interface UserCertificationUpdate {
  certification_name?: string | null;
  issuer?: string | null;
  issued_date?: string | null;
  expiry_date?: string | null;
  certification_number?: string | null;
  notes?: string | null;
  verified?: boolean | null;
}

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/** GET /api/users/me/certifications */
export async function getMyCertifications(): Promise<UserCertification[]> {
  const { data } = await apiClient.get<UserCertification[]>('/api/users/me/certifications');
  return data;
}

/** POST /api/users/me/certifications */
export async function addMyCertification(
  payload: UserCertificationCreate,
): Promise<UserCertification> {
  const { data } = await apiClient.post<UserCertification>(
    '/api/users/me/certifications',
    payload,
  );
  return data;
}

/** PATCH /api/users/me/certifications/:certificationId */
export async function updateMyCertification(
  certificationId: string,
  updates: UserCertificationUpdate,
): Promise<UserCertification> {
  const { data } = await apiClient.patch<UserCertification>(
    `/api/users/me/certifications/${certificationId}`,
    updates,
  );
  return data;
}

/** DELETE /api/users/me/certifications/:certificationId */
export async function deleteMyCertification(certificationId: string): Promise<void> {
  await apiClient.delete(`/api/users/me/certifications/${certificationId}`);
}

/** GET /api/users/:userId/certifications */
export async function getUserCertifications(userId: string): Promise<UserCertification[]> {
  const { data } = await apiClient.get<UserCertification[]>(
    `/api/users/${userId}/certifications`,
  );
  return data;
}
