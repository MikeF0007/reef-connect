import React, { useState, useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLocalStorage } from '../hooks/useStorage';
import { ActivityItem, DiveLog, Friendship, User, SpeciesTag } from '../types';
import { mockSpeciesCatalog } from '../data/mockSpecies';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Heart, MessageCircle, Send } from 'lucide-react';

export function ActivityFeedPage() {
  const { user } = useAuth();
  const [diveLogs] = useLocalStorage<DiveLog[]>('reefconnect_dives', []);
  const [friendships] = useLocalStorage<Friendship[]>('reefconnect_friendships', []);
  const [users] = useLocalStorage<(User & { password: string })[]>('reefconnect_users', []);
  const [speciesTags] = useLocalStorage<SpeciesTag[]>('reefconnect_species_tags', []);
  const [activities, setActivities] = useLocalStorage<ActivityItem[]>(
    'reefconnect_activities',
    []
  );
  const [commentText, setCommentText] = useState<{ [key: string]: string }>({});

  if (!user) return null;

  // Get friend IDs
  const myFriendships = friendships.filter(
    (f) => f.userId1 === user.id || f.userId2 === user.id
  );
  const friendIds = new Set(
    myFriendships.map((f) => (f.userId1 === user.id ? f.userId2 : f.userId1))
  );

  // Generate activities from dive logs and species discoveries
  const generatedActivities = useMemo(() => {
    const items: ActivityItem[] = [];

    // Recent dives from friends
    diveLogs
      .filter((dive) => friendIds.has(dive.userId))
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
      .slice(0, 10)
      .forEach((dive) => {
        const existing = activities.find((a) => a.relatedId === dive.id);
        if (!existing) {
          items.push({
            id: `dive-${dive.id}`,
            userId: dive.userId,
            type: 'dive',
            content: `logged a dive at ${dive.location}${dive.site ? ` - ${dive.site}` : ''}`,
            relatedId: dive.id,
            createdAt: dive.createdAt,
            likes: [],
            comments: [],
          });
        }
      });

    // Recent species discoveries from friends
    const friendSpeciesTags = speciesTags.filter((tag) => friendIds.has(tag.userId));
    const speciesDiscoveries = new Map<string, SpeciesTag>();
    friendSpeciesTags.forEach((tag) => {
      const key = `${tag.userId}-${tag.speciesId}`;
      if (!speciesDiscoveries.has(key)) {
        speciesDiscoveries.set(key, tag);
      }
    });

    Array.from(speciesDiscoveries.values())
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
      .slice(0, 5)
      .forEach((tag) => {
        const species = mockSpeciesCatalog.find((s) => s.id === tag.speciesId);
        if (species) {
          const existing = activities.find((a) => a.relatedId === `${tag.userId}-${tag.speciesId}`);
          if (!existing) {
            items.push({
              id: `species-${tag.id}`,
              userId: tag.userId,
              type: 'species',
              content: `discovered a ${species.commonName}`,
              relatedId: `${tag.userId}-${tag.speciesId}`,
              createdAt: tag.createdAt,
              likes: [],
              comments: [],
            });
          }
        }
      });

    return items;
  }, [diveLogs, speciesTags, friendIds, activities]);

  // Merge with stored activities and sort
  const allActivities = [...activities, ...generatedActivities]
    .filter((activity, index, self) => self.findIndex((a) => a.id === activity.id) === index)
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

  const getUser = (userId: string) => {
    const foundUser = users.find((u) => u.id === userId);
    if (!foundUser) return null;
    const { password, ...userWithoutPassword } = foundUser;
    return userWithoutPassword;
  };

  const handleLike = (activityId: string) => {
    setActivities(
      allActivities.map((activity) => {
        if (activity.id === activityId) {
          const likes = activity.likes.includes(user.id)
            ? activity.likes.filter((id) => id !== user.id)
            : [...activity.likes, user.id];
          return { ...activity, likes };
        }
        return activity;
      })
    );
  };

  const handleComment = (activityId: string) => {
    const text = commentText[activityId]?.trim();
    if (!text) return;

    setActivities(
      allActivities.map((activity) => {
        if (activity.id === activityId) {
          return {
            ...activity,
            comments: [
              ...activity.comments,
              {
                id: crypto.randomUUID(),
                userId: user.id,
                username: user.username,
                content: text,
                createdAt: new Date().toISOString(),
              },
            ],
          };
        }
        return activity;
      })
    );

    setCommentText({ ...commentText, [activityId]: '' });
  };

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-6">
      <div>
        <h1>Activity Feed</h1>
        <p className="text-sm text-gray-600">See what your friends are up to</p>
      </div>

      {allActivities.length === 0 ? (
        <Card className="p-12 text-center">
          <div className="text-gray-600">
            <p>No activities yet</p>
            <p className="text-sm mt-2">Add friends to see their diving activities</p>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {allActivities.map((activity) => {
            const activityUser = getUser(activity.userId);
            if (!activityUser) return null;

            const isLiked = activity.likes.includes(user.id);

            return (
              <Card key={activity.id}>
                <CardContent className="p-4 space-y-3">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                      <span>{activityUser.username[0].toUpperCase()}</span>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm">
                        <span className="font-semibold">{activityUser.username}</span>{' '}
                        {activity.content}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(activity.createdAt).toLocaleDateString()}{' '}
                        {new Date(activity.createdAt).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </p>
                    </div>
                    <Badge variant="secondary">{activity.type}</Badge>
                  </div>

                  <div className="flex items-center gap-4 text-sm">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleLike(activity.id)}
                      className={isLiked ? 'text-red-600' : ''}
                    >
                      <Heart size={16} fill={isLiked ? 'currentColor' : 'none'} />
                      <span className="ml-1">{activity.likes.length}</span>
                    </Button>
                    <Button variant="ghost" size="sm">
                      <MessageCircle size={16} />
                      <span className="ml-1">{activity.comments.length}</span>
                    </Button>
                  </div>

                  {activity.comments.length > 0 && (
                    <div className="space-y-2 pt-2 border-t">
                      {activity.comments.map((comment) => (
                        <div key={comment.id} className="flex gap-2 text-sm">
                          <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
                            <span className="text-xs">{comment.username[0].toUpperCase()}</span>
                          </div>
                          <div className="flex-1">
                            <p>
                              <span className="font-semibold">{comment.username}</span>{' '}
                              {comment.content}
                            </p>
                            <p className="text-xs text-gray-500">
                              {new Date(comment.createdAt).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Input
                      placeholder="Add a comment..."
                      value={commentText[activity.id] || ''}
                      onChange={(e) =>
                        setCommentText({ ...commentText, [activity.id]: e.target.value })
                      }
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          handleComment(activity.id);
                        }
                      }}
                      className="text-sm"
                    />
                    <Button size="sm" onClick={() => handleComment(activity.id)}>
                      <Send size={16} />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
