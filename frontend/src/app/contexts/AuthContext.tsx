import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from 'react';
import { User } from '../types';
import { loginUser } from '../../api/authApi';
import { updateMyProfile } from '../../api/userApi';
import { TOKEN_KEY } from '../../lib/apiClient';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (
    email: string,
    password: string,
    username: string,
  ) => Promise<boolean>;
  logout: () => void;
  updateProfile: (updates: Partial<User>) => Promise<void>;
  isAuthenticated: boolean;
  isLoading: boolean;
  authError: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  useEffect(() => {
    // Restore session from localStorage on mount
    const storedUser = localStorage.getItem('reefconnect_user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    setAuthError(null);
    try {
      const { user: loggedInUser, token } = await loginUser(email, password);
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem('reefconnect_user', JSON.stringify(loggedInUser));
      setUser(loggedInUser);
      return true;
    } catch (err: any) {
      const message = err.response?.data?.error ?? 'Invalid email or password';
      setAuthError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (
    email: string,
    password: string,
    username: string,
  ): Promise<boolean> => {
    const users = JSON.parse(localStorage.getItem('reefconnect_users') || '[]');

    // Check if user exists
    if (users.some((u: any) => u.email === email)) {
      return false;
    }

    const newUser: User & { password: string } = {
      id: crypto.randomUUID(),
      email,
      password,
      username,
      bio: '',
      certifications: [],
      createdAt: new Date().toISOString(),
      privacySettings: {
        profileVisibility: 'public',
        diveLogsVisibility: 'public',
        mediaVisibility: 'public',
        statsVisibility: 'public',
      },
    };

    users.push(newUser);
    localStorage.setItem('reefconnect_users', JSON.stringify(users));

    const { password: _, ...userWithoutPassword } = newUser;
    setUser(userWithoutPassword);
    localStorage.setItem(
      'reefconnect_user',
      JSON.stringify(userWithoutPassword),
    );
    return true;
  };

  const logout = () => {
    setUser(null);
    setAuthError(null);
    localStorage.removeItem('reefconnect_user');
    localStorage.removeItem(TOKEN_KEY);
  };

  const updateProfile = async (updates: Partial<User>): Promise<void> => {
    if (!user) return;

    // Persist bio to the backend profile API; other fields (username,
    // certifications, privacySettings) have no backend route yet.
    if (updates.bio !== undefined) {
      await updateMyProfile({ bio: updates.bio ?? null });
    }

    const updatedUser = { ...user, ...updates };
    setUser(updatedUser);
    localStorage.setItem('reefconnect_user', JSON.stringify(updatedUser));
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        register,
        logout,
        updateProfile,
        isAuthenticated: !!user,
        isLoading,
        authError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
