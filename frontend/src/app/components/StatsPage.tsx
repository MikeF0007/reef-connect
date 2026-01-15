import React, { useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLocalStorage } from '../hooks/useStorage';
import { DiveLog, Media, SpeciesTag, UserBadge } from '../types';
import { badges } from '../data/mockBadges';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Award, Fish, Gauge, Clock, Camera, Trophy } from 'lucide-react';

export function StatsPage() {
  const { user } = useAuth();
  const [diveLogs] = useLocalStorage<DiveLog[]>('reefconnect_dives', []);
  const [media] = useLocalStorage<Media[]>('reefconnect_media', []);
  const [speciesTags] = useLocalStorage<SpeciesTag[]>('reefconnect_species_tags', []);
  const [userBadges, setUserBadges] = useLocalStorage<UserBadge[]>('reefconnect_user_badges', []);

  if (!user) return null;

  // Calculate stats
  const stats = useMemo(() => {
    const userDives = diveLogs.filter((dive) => dive.userId === user.id);
    const userMedia = media.filter((m) => m.userId === user.id);
    const userTags = speciesTags.filter((tag) => tag.userId === user.id);

    const uniqueSpecies = new Set(userTags.map((tag) => tag.speciesId));
    const deepestDive = userDives.reduce((max, dive) => Math.max(max, dive.depth), 0);
    const totalDiveTime = userDives.reduce((sum, dive) => sum + dive.duration, 0);

    return {
      totalDives: userDives.length,
      totalSpecies: uniqueSpecies.size,
      deepestDive,
      totalDiveTime,
      totalMedia: userMedia.length,
      totalBadges: userBadges.filter((ub) => ub.userId === user.id).length,
    };
  }, [diveLogs, media, speciesTags, user.id, userBadges]);

  // Check and award badges
  useMemo(() => {
    const newBadges: UserBadge[] = [];

    badges.forEach((badge) => {
      const alreadyEarned = userBadges.some(
        (ub) => ub.userId === user.id && ub.badgeId === badge.id
      );
      if (alreadyEarned) return;

      let earned = false;
      switch (badge.category) {
        case 'dives':
          earned = stats.totalDives >= badge.requirement;
          break;
        case 'depth':
          earned = stats.deepestDive >= badge.requirement;
          break;
        case 'species':
          earned = stats.totalSpecies >= badge.requirement;
          break;
        case 'media':
          earned = stats.totalMedia >= badge.requirement;
          break;
      }

      if (earned) {
        newBadges.push({
          userId: user.id,
          badgeId: badge.id,
          earnedAt: new Date().toISOString(),
        });
      }
    });

    if (newBadges.length > 0) {
      setUserBadges([...userBadges, ...newBadges]);
    }
  }, [stats, user.id, userBadges, setUserBadges]);

  // Dive depth over time
  const depthData = diveLogs
    .filter((dive) => dive.userId === user.id)
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .map((dive, index) => ({
      dive: index + 1,
      depth: dive.depth,
      date: new Date(dive.date).toLocaleDateString(),
    }));

  // Dives per month
  const divesPerMonth = diveLogs
    .filter((dive) => dive.userId === user.id)
    .reduce((acc, dive) => {
      const month = new Date(dive.date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
      });
      acc[month] = (acc[month] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

  const monthData = Object.entries(divesPerMonth).map(([month, count]) => ({
    month,
    dives: count,
  }));

  const earnedBadges = badges.filter((badge) =>
    userBadges.some((ub) => ub.userId === user.id && ub.badgeId === badge.id)
  );

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <div>
        <h1>Statistics</h1>
        <p className="text-sm text-gray-600">Your diving achievements and progress</p>
      </div>

      {/* Key Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="flex justify-center mb-2">
              <div className="p-2 bg-blue-100 rounded-full">
                <Gauge className="text-blue-600" size={24} />
              </div>
            </div>
            <p className="text-2xl font-semibold">{stats.totalDives}</p>
            <p className="text-xs text-gray-600">Total Dives</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <div className="flex justify-center mb-2">
              <div className="p-2 bg-green-100 rounded-full">
                <Fish className="text-green-600" size={24} />
              </div>
            </div>
            <p className="text-2xl font-semibold">{stats.totalSpecies}</p>
            <p className="text-xs text-gray-600">Species</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <div className="flex justify-center mb-2">
              <div className="p-2 bg-purple-100 rounded-full">
                <Gauge className="text-purple-600" size={24} />
              </div>
            </div>
            <p className="text-2xl font-semibold">{stats.deepestDive}m</p>
            <p className="text-xs text-gray-600">Deepest</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <div className="flex justify-center mb-2">
              <div className="p-2 bg-orange-100 rounded-full">
                <Clock className="text-orange-600" size={24} />
              </div>
            </div>
            <p className="text-2xl font-semibold">{stats.totalDiveTime}</p>
            <p className="text-xs text-gray-600">Minutes</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <div className="flex justify-center mb-2">
              <div className="p-2 bg-pink-100 rounded-full">
                <Camera className="text-pink-600" size={24} />
              </div>
            </div>
            <p className="text-2xl font-semibold">{stats.totalMedia}</p>
            <p className="text-xs text-gray-600">Photos</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <div className="flex justify-center mb-2">
              <div className="p-2 bg-yellow-100 rounded-full">
                <Trophy className="text-yellow-600" size={24} />
              </div>
            </div>
            <p className="text-2xl font-semibold">{stats.totalBadges}</p>
            <p className="text-xs text-gray-600">Badges</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid md:grid-cols-2 gap-6">
        {depthData.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Dive Depth History</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={depthData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="dive" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="depth" stroke="#2563eb" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {monthData.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Dives Per Month</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={monthData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="dives" fill="#2563eb" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Badges */}
      <Card>
        <CardHeader>
          <CardTitle>Badges & Achievements</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {earnedBadges.map((badge) => (
              <div
                key={badge.id}
                className="flex flex-col items-center text-center p-4 bg-gradient-to-br from-yellow-50 to-orange-50 rounded-lg"
              >
                <div className="w-16 h-16 bg-gradient-to-br from-yellow-400 to-orange-400 rounded-full flex items-center justify-center mb-2">
                  <Award className="text-white" size={32} />
                </div>
                <h3 className="text-sm">{badge.name}</h3>
                <p className="text-xs text-gray-600">{badge.description}</p>
              </div>
            ))}
            {earnedBadges.length === 0 && (
              <div className="col-span-full text-center py-8 text-gray-500">
                <Trophy size={40} className="mx-auto mb-2 opacity-50" />
                <p>No badges earned yet. Keep diving!</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
