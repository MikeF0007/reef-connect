import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLocalStorage } from '../hooks/useStorage';
import { FriendRequest, Friendship, User } from '../types';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { UserPlus, Check, X, Users } from 'lucide-react';

export function FriendsPage() {
  const { user } = useAuth();
  const [friendRequests, setFriendRequests] = useLocalStorage<FriendRequest[]>(
    'reefconnect_friend_requests',
    []
  );
  const [friendships, setFriendships] = useLocalStorage<Friendship[]>(
    'reefconnect_friendships',
    []
  );
  const [users] = useLocalStorage<(User & { password: string })[]>('reefconnect_users', []);
  const [searchQuery, setSearchQuery] = useState('');

  if (!user) return null;

  const myFriendships = friendships.filter(
    (f) => f.userId1 === user.id || f.userId2 === user.id
  );

  const friendIds = new Set(
    myFriendships.map((f) => (f.userId1 === user.id ? f.userId2 : f.userId1))
  );

  const incomingRequests = friendRequests.filter(
    (r) => r.toUserId === user.id && r.status === 'pending'
  );

  const outgoingRequests = friendRequests.filter(
    (r) => r.fromUserId === user.id && r.status === 'pending'
  );

  const friends = users
    .filter((u) => friendIds.has(u.id))
    .map(({ password, ...userWithoutPassword }) => userWithoutPassword);

  const potentialFriends = users
    .filter(
      (u) =>
        u.id !== user.id &&
        !friendIds.has(u.id) &&
        !outgoingRequests.some((r) => r.toUserId === u.id) &&
        (u.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
          u.email.toLowerCase().includes(searchQuery.toLowerCase()))
    )
    .map(({ password, ...userWithoutPassword }) => userWithoutPassword);

  const handleSendRequest = (toUserId: string) => {
    const newRequest: FriendRequest = {
      id: crypto.randomUUID(),
      fromUserId: user.id,
      toUserId,
      status: 'pending',
      createdAt: new Date().toISOString(),
    };
    setFriendRequests([...friendRequests, newRequest]);
  };

  const handleAcceptRequest = (requestId: string) => {
    const request = friendRequests.find((r) => r.id === requestId);
    if (!request) return;

    // Create friendship
    const newFriendship: Friendship = {
      id: crypto.randomUUID(),
      userId1: request.fromUserId,
      userId2: request.toUserId,
      createdAt: new Date().toISOString(),
    };
    setFriendships([...friendships, newFriendship]);

    // Update request status
    setFriendRequests(
      friendRequests.map((r) => (r.id === requestId ? { ...r, status: 'accepted' as const } : r))
    );
  };

  const handleDeclineRequest = (requestId: string) => {
    setFriendRequests(
      friendRequests.map((r) =>
        r.id === requestId ? { ...r, status: 'declined' as const } : r
      )
    );
  };

  const getUser = (userId: string) => {
    const foundUser = users.find((u) => u.id === userId);
    if (!foundUser) return null;
    const { password, ...userWithoutPassword } = foundUser;
    return userWithoutPassword;
  };

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1>Friends</h1>
          <p className="text-sm text-gray-600">{friends.length} friends</p>
        </div>
      </div>

      <Tabs defaultValue="friends">
        <TabsList>
          <TabsTrigger value="friends">
            My Friends
            <Badge variant="secondary" className="ml-2">
              {friends.length}
            </Badge>
          </TabsTrigger>
          <TabsTrigger value="requests">
            Requests
            {incomingRequests.length > 0 && (
              <Badge className="ml-2">{incomingRequests.length}</Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="find">Find Friends</TabsTrigger>
        </TabsList>

        <TabsContent value="friends" className="space-y-4">
          {friends.length === 0 ? (
            <Card className="p-12 text-center">
              <div className="flex flex-col items-center gap-4">
                <div className="w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center">
                  <Users size={40} className="text-blue-600" />
                </div>
                <div>
                  <h3>No friends yet</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Find and add friends to share your diving adventures
                  </p>
                </div>
              </div>
            </Card>
          ) : (
            <div className="grid gap-4">
              {friends.map((friend) => (
                <Card key={friend.id}>
                  <CardContent className="p-4 flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                      <span className="text-xl">{friend.username[0].toUpperCase()}</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-sm">{friend.username}</h3>
                      <p className="text-xs text-gray-500">{friend.email}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="requests" className="space-y-4">
          {incomingRequests.length === 0 && outgoingRequests.length === 0 ? (
            <Card className="p-12 text-center">
              <p className="text-gray-600">No pending friend requests</p>
            </Card>
          ) : (
            <>
              {incomingRequests.length > 0 && (
                <div>
                  <h3 className="mb-3">Incoming Requests</h3>
                  <div className="grid gap-4">
                    {incomingRequests.map((request) => {
                      const fromUser = getUser(request.fromUserId);
                      if (!fromUser) return null;
                      return (
                        <Card key={request.id}>
                          <CardContent className="p-4 flex items-center gap-4">
                            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                              <span className="text-xl">
                                {fromUser.username[0].toUpperCase()}
                              </span>
                            </div>
                            <div className="flex-1">
                              <h3 className="text-sm">{fromUser.username}</h3>
                              <p className="text-xs text-gray-500">{fromUser.email}</p>
                            </div>
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                onClick={() => handleAcceptRequest(request.id)}
                              >
                                <Check size={16} />
                                <span className="ml-1">Accept</span>
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleDeclineRequest(request.id)}
                              >
                                <X size={16} />
                                <span className="ml-1">Decline</span>
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                </div>
              )}

              {outgoingRequests.length > 0 && (
                <div>
                  <h3 className="mb-3">Sent Requests</h3>
                  <div className="grid gap-4">
                    {outgoingRequests.map((request) => {
                      const toUser = getUser(request.toUserId);
                      if (!toUser) return null;
                      return (
                        <Card key={request.id}>
                          <CardContent className="p-4 flex items-center gap-4">
                            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                              <span className="text-xl">{toUser.username[0].toUpperCase()}</span>
                            </div>
                            <div className="flex-1">
                              <h3 className="text-sm">{toUser.username}</h3>
                              <p className="text-xs text-gray-500">{toUser.email}</p>
                            </div>
                            <Badge variant="secondary">Pending</Badge>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                </div>
              )}
            </>
          )}
        </TabsContent>

        <TabsContent value="find" className="space-y-4">
          <Input
            placeholder="Search users..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <div className="grid gap-4">
            {potentialFriends.map((potentialFriend) => (
              <Card key={potentialFriend.id}>
                <CardContent className="p-4 flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                    <span className="text-xl">
                      {potentialFriend.username[0].toUpperCase()}
                    </span>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-sm">{potentialFriend.username}</h3>
                    <p className="text-xs text-gray-500">{potentialFriend.email}</p>
                  </div>
                  <Button size="sm" onClick={() => handleSendRequest(potentialFriend.id)}>
                    <UserPlus size={16} />
                    <span className="ml-1">Add Friend</span>
                  </Button>
                </CardContent>
              </Card>
            ))}
            {searchQuery && potentialFriends.length === 0 && (
              <Card className="p-8 text-center">
                <p className="text-gray-600">No users found</p>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
