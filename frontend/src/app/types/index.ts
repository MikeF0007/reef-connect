// Core types for ReefConnect

export interface User {
  id: string;
  email: string;
  username: string;
  bio?: string;
  avatar?: string;
  certifications: string[];
  createdAt: string;
  privacySettings: PrivacySettings;
}

export interface PrivacySettings {
  profileVisibility: 'public' | 'friends' | 'private';
  diveLogsVisibility: 'public' | 'friends' | 'private';
  mediaVisibility: 'public' | 'friends' | 'private';
  statsVisibility: 'public' | 'friends' | 'private';
}

export interface DiveLog {
  id: string;
  userId: string;
  date: string;
  time: string;
  location: string;
  site?: string;
  depth: number; // meters
  duration: number; // minutes
  waterTemp?: number;
  airTemp?: number;
  visibility?: number;
  conditions?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Media {
  id: string;
  userId: string;
  diveLogId: string;
  type: 'photo' | 'video';
  url: string;
  thumbnailUrl: string;
  caption?: string;
  uploadedAt: string;
}

export interface Species {
  id: string;
  commonName: string;
  scientificName: string;
  category: string;
  imageUrl?: string;
}

export interface SpeciesTag {
  id: string;
  mediaId: string;
  speciesId: string;
  userId: string;
  createdAt: string;
}

export interface ScubaDexEntry {
  speciesId: string;
  species: Species;
  firstSeenDate: string;
  encounterCount: number;
  mediaIds: string[];
}

export interface FriendRequest {
  id: string;
  fromUserId: string;
  toUserId: string;
  status: 'pending' | 'accepted' | 'declined';
  createdAt: string;
}

export interface Friendship {
  id: string;
  userId1: string;
  userId2: string;
  createdAt: string;
}

export interface ActivityItem {
  id: string;
  userId: string;
  type: 'dive' | 'species' | 'badge' | 'media';
  content: string;
  relatedId?: string;
  createdAt: string;
  likes: string[]; // user IDs who liked
  comments: Comment[];
}

export interface Comment {
  id: string;
  userId: string;
  username: string;
  content: string;
  createdAt: string;
}

export interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: 'dives' | 'depth' | 'species' | 'media' | 'social';
  requirement: number;
}

export interface UserBadge {
  userId: string;
  badgeId: string;
  earnedAt: string;
}

export interface UserStats {
  userId: string;
  totalDives: number;
  totalSpecies: number;
  deepestDive: number;
  totalDiveTime: number;
  totalMedia: number;
  totalBadges: number;
}

export interface Notification {
  id: string;
  userId: string;
  type: 'friend_request' | 'like' | 'comment' | 'badge';
  content: string;
  relatedId?: string;
  read: boolean;
  createdAt: string;
}
