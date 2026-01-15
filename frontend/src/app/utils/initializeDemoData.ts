import { User, DiveLog, Media, SpeciesTag } from '../types';

export function initializeDemoData() {
  // Check if already initialized
  if (localStorage.getItem('reefconnect_demo_initialized')) {
    return;
  }

  // Create demo users
  const demoUsers: (User & { password: string })[] = [
    {
      id: 'demo-user-1',
      email: 'demo@reefconnect.com',
      password: 'demo',
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
    {
      id: 'demo-user-2',
      email: 'sarah@example.com',
      password: 'password',
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
    {
      id: 'demo-user-3',
      email: 'mike@example.com',
      password: 'password',
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
  ];

  // Create demo dive logs
  const demoDiveLogs: DiveLog[] = [
    {
      id: 'dive-1',
      userId: 'demo-user-1',
      date: '2024-12-15',
      time: '10:30',
      location: 'Great Barrier Reef, Australia',
      site: 'Cod Hole',
      depth: 28.5,
      duration: 45,
      waterTemp: 26,
      visibility: 30,
      conditions: 'Calm seas, slight current',
      notes: 'Amazing dive! Saw a giant potato cod and many colorful reef fish.',
      createdAt: new Date('2024-12-15').toISOString(),
      updatedAt: new Date('2024-12-15').toISOString(),
    },
    {
      id: 'dive-2',
      userId: 'demo-user-2',
      date: '2024-12-20',
      time: '14:00',
      location: 'Maldives',
      site: 'Manta Point',
      depth: 18.0,
      duration: 50,
      waterTemp: 28,
      visibility: 25,
      conditions: 'Perfect conditions',
      notes: 'Three manta rays circled us for the entire dive. Unforgettable experience!',
      createdAt: new Date('2024-12-20').toISOString(),
      updatedAt: new Date('2024-12-20').toISOString(),
    },
    {
      id: 'dive-3',
      userId: 'demo-user-3',
      date: '2024-12-18',
      time: '09:00',
      location: 'Red Sea, Egypt',
      site: 'Ras Mohammed',
      depth: 32.0,
      duration: 42,
      waterTemp: 24,
      visibility: 35,
      conditions: 'Clear, moderate current',
      notes: 'Deep wall dive with incredible coral formations and schooling fish.',
      createdAt: new Date('2024-12-18').toISOString(),
      updatedAt: new Date('2024-12-18').toISOString(),
    },
    {
      id: 'dive-4',
      userId: 'demo-user-2',
      date: '2024-12-10',
      time: '11:00',
      location: 'Bali, Indonesia',
      site: 'USS Liberty Wreck',
      depth: 22.0,
      duration: 55,
      waterTemp: 27,
      visibility: 20,
      conditions: 'Good visibility',
      notes: 'Historic wreck covered in soft corals. Saw giant barracuda and schools of jacks.',
      createdAt: new Date('2024-12-10').toISOString(),
      updatedAt: new Date('2024-12-10').toISOString(),
    },
    {
      id: 'dive-5',
      userId: 'demo-user-1',
      date: '2024-11-25',
      time: '08:00',
      location: 'Great Barrier Reef, Australia',
      site: 'Flynn Reef',
      depth: 15.0,
      duration: 48,
      waterTemp: 25,
      visibility: 28,
      conditions: 'Excellent',
      notes: 'Beautiful shallow reef dive with lots of turtles and clownfish.',
      createdAt: new Date('2024-11-25').toISOString(),
      updatedAt: new Date('2024-11-25').toISOString(),
    },
  ];

  // Create demo media
  const demoMedia: Media[] = [
    {
      id: 'media-1',
      userId: 'demo-user-1',
      diveLogId: 'dive-1',
      type: 'photo',
      url: 'https://images.unsplash.com/photo-1628371217613-714161455f6b?w=800',
      thumbnailUrl: 'https://images.unsplash.com/photo-1628371217613-714161455f6b?w=400',
      caption: 'Vibrant coral reef',
      uploadedAt: new Date('2024-12-15').toISOString(),
    },
    {
      id: 'media-2',
      userId: 'demo-user-2',
      diveLogId: 'dive-2',
      type: 'photo',
      url: 'https://images.unsplash.com/photo-1544552866-d3ed42536cfd?w=800',
      thumbnailUrl: 'https://images.unsplash.com/photo-1544552866-d3ed42536cfd?w=400',
      caption: 'Manta ray encounter',
      uploadedAt: new Date('2024-12-20').toISOString(),
    },
  ];

  // Create demo species tags
  const demoSpeciesTags: SpeciesTag[] = [
    {
      id: 'tag-1',
      mediaId: 'media-1',
      speciesId: 'sp-001', // Clownfish
      userId: 'demo-user-1',
      createdAt: new Date('2024-12-15').toISOString(),
    },
    {
      id: 'tag-2',
      mediaId: 'media-2',
      speciesId: 'sp-003', // Manta Ray
      userId: 'demo-user-2',
      createdAt: new Date('2024-12-20').toISOString(),
    },
  ];

  // Save to localStorage
  localStorage.setItem('reefconnect_users', JSON.stringify(demoUsers));
  localStorage.setItem('reefconnect_dives', JSON.stringify(demoDiveLogs));
  localStorage.setItem('reefconnect_media', JSON.stringify(demoMedia));
  localStorage.setItem('reefconnect_species_tags', JSON.stringify(demoSpeciesTags));
  localStorage.setItem('reefconnect_demo_initialized', 'true');
}