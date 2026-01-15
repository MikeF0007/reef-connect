import React, { useMemo, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLocalStorage } from '../hooks/useStorage';
import { DiveLog, Media, SpeciesTag, Friendship, User, UserStats } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Trophy, Medal, Award } from 'lucide-react';

type LeaderboardType = 'all' | 'friends';

export function LeaderboardPage() {
  const { user } = useAuth();
  const [diveLogs] = useLocalStorage<DiveLog[]>('reefconnect_dives', []);
  const [media] = useLocalStorage<Media[]>('reefconnect_media', []);
  const [speciesTags] = useLocalStorage<SpeciesTag[]>('reefconnect_species_tags', []);
  const [friendships] = useLocalStorage<Friendship[]>('reefconnect_friendships', []);
  const [users] = useLocalStorage<(User & { password: string })[]>('reefconnect_users', []);
  const [leaderboardType, setLeaderboardType] = useState<LeaderboardType>('all');
  const [metric, setMetric] = useState<keyof UserStats>('totalDives');

  if (!user) return null;

  // Get friend IDs
  const myFriendships = friendships.filter(
    (f) => f.userId1 === user.id || f.userId2 === user.id
  );
  const friendIds = new Set(
    myFriendships.map((f) => (f.userId1 === user.id ? f.userId2 : f.userId1))
  );
  friendIds.add(user.id); // Include current user

  // Calculate stats for all users
  const userStats = useMemo(() => {
    const stats: UserStats[] = [];

    users.forEach((u) => {
      const userDives = diveLogs.filter((dive) => dive.userId === u.id);
      const userMedia = media.filter((m) => m.userId === u.id);
      const userTags = speciesTags.filter((tag) => tag.userId === u.id);
      const uniqueSpecies = new Set(userTags.map((tag) => tag.speciesId));

      stats.push({
        userId: u.id,
        totalDives: userDives.length,
        totalSpecies: uniqueSpecies.size,
        deepestDive: userDives.reduce((max, dive) => Math.max(max, dive.depth), 0),
        totalDiveTime: userDives.reduce((sum, dive) => sum + dive.duration, 0),
        totalMedia: userMedia.length,
        totalBadges: 0, // Would calculate from user badges
      });
    });

    return stats;
  }, [users, diveLogs, media, speciesTags]);

  const filteredStats = useMemo(() => {
    const filtered =
      leaderboardType === 'friends'
        ? userStats.filter((s) => friendIds.has(s.userId))
        : userStats;

    return filtered.sort((a, b) => b[metric] - a[metric]);
  }, [userStats, leaderboardType, metric, friendIds]);

  const getUser = (userId: string) => {
    const foundUser = users.find((u) => u.id === userId);
    if (!foundUser) return null;
    const { password, ...userWithoutPassword } = foundUser;
    return userWithoutPassword;
  };

  const getRankIcon = (index: number) => {
    if (index === 0) return <Trophy className="text-yellow-500" size={24} />;
    if (index === 1) return <Medal className="text-gray-400" size={24} />;
    if (index === 2) return <Award className="text-orange-600" size={24} />;
    return null;
  };

  const getMetricLabel = (metric: keyof UserStats) => {
    switch (metric) {
      case 'totalDives':
        return 'Total Dives';
      case 'totalSpecies':
        return 'Species Discovered';
      case 'deepestDive':
        return 'Deepest Dive (m)';
      case 'totalDiveTime':
        return 'Total Dive Time (min)';
      default:
        return metric;
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      <div>
        <h1>Leaderboards</h1>
        <p className="text-sm text-gray-600">Compare your diving achievements</p>
      </div>

      <Tabs value={leaderboardType} onValueChange={(v) => setLeaderboardType(v as LeaderboardType)}>
        <TabsList>
          <TabsTrigger value="all">Global</TabsTrigger>
          <TabsTrigger value="friends">Friends</TabsTrigger>
        </TabsList>

        <TabsContent value={leaderboardType} className="space-y-4">
          <div className="flex gap-2 flex-wrap">
            <Badge
              variant={metric === 'totalDives' ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => setMetric('totalDives')}
            >
              Total Dives
            </Badge>
            <Badge
              variant={metric === 'totalSpecies' ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => setMetric('totalSpecies')}
            >
              Species
            </Badge>
            <Badge
              variant={metric === 'deepestDive' ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => setMetric('deepestDive')}
            >
              Deepest Dive
            </Badge>
            <Badge
              variant={metric === 'totalDiveTime' ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => setMetric('totalDiveTime')}
            >
              Dive Time
            </Badge>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>{getMetricLabel(metric)}</CardTitle>
            </CardHeader>
            <CardContent>
              {filteredStats.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>No data available</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredStats.map((stats, index) => {
                    const statsUser = getUser(stats.userId);
                    if (!statsUser) return null;

                    const isCurrentUser = stats.userId === user.id;

                    return (
                      <div
                        key={stats.userId}
                        className={`flex items-center gap-4 p-3 rounded-lg ${
                          isCurrentUser ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50'
                        }`}
                      >
                        <div className="w-12 text-center font-semibold text-gray-600">
                          {getRankIcon(index) || `#${index + 1}`}
                        </div>
                        <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                          <span className="text-lg">{statsUser.username[0].toUpperCase()}</span>
                        </div>
                        <div className="flex-1">
                          <h3 className="text-sm">
                            {statsUser.username}
                            {isCurrentUser && (
                              <Badge variant="secondary" className="ml-2">
                                You
                              </Badge>
                            )}
                          </h3>
                        </div>
                        <div className="text-right">
                          <p className="text-xl font-semibold">{stats[metric]}</p>
                          {metric === 'deepestDive' && <p className="text-xs text-gray-500">meters</p>}
                          {metric === 'totalDiveTime' && (
                            <p className="text-xs text-gray-500">minutes</p>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
