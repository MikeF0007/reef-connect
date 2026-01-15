import React, { useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLocalStorage } from '../hooks/useStorage';
import { Notification, FriendRequest, ActivityItem } from '../types';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Bell, Check } from 'lucide-react';

export function NotificationsPage() {
  const { user } = useAuth();
  const [notifications, setNotifications] = useLocalStorage<Notification[]>(
    'reefconnect_notifications',
    []
  );
  const [friendRequests] = useLocalStorage<FriendRequest[]>('reefconnect_friend_requests', []);
  const [activities] = useLocalStorage<ActivityItem[]>('reefconnect_activities', []);

  if (!user) return null;

  // Generate notifications from friend requests and activity
  const generatedNotifications = useMemo(() => {
    const items: Notification[] = [];

    // Friend requests
    friendRequests
      .filter((r) => r.toUserId === user.id && r.status === 'pending')
      .forEach((request) => {
        const existing = notifications.find((n) => n.relatedId === request.id);
        if (!existing) {
          items.push({
            id: `fr-${request.id}`,
            userId: user.id,
            type: 'friend_request',
            content: 'You have a new friend request',
            relatedId: request.id,
            read: false,
            createdAt: request.createdAt,
          });
        }
      });

    // Likes on activities
    activities
      .filter((a) => a.userId === user.id && a.likes.length > 0)
      .forEach((activity) => {
        const existing = notifications.find((n) => n.relatedId === activity.id && n.type === 'like');
        if (!existing && activity.likes.length > 0) {
          items.push({
            id: `like-${activity.id}`,
            userId: user.id,
            type: 'like',
            content: `${activity.likes.length} ${activity.likes.length === 1 ? 'person' : 'people'} liked your activity`,
            relatedId: activity.id,
            read: false,
            createdAt: activity.createdAt,
          });
        }
      });

    // Comments on activities
    activities
      .filter((a) => a.userId === user.id && a.comments.length > 0)
      .forEach((activity) => {
        activity.comments.forEach((comment) => {
          if (comment.userId !== user.id) {
            const existing = notifications.find(
              (n) => n.relatedId === comment.id && n.type === 'comment'
            );
            if (!existing) {
              items.push({
                id: `comment-${comment.id}`,
                userId: user.id,
                type: 'comment',
                content: `${comment.username} commented on your activity`,
                relatedId: comment.id,
                read: false,
                createdAt: comment.createdAt,
              });
            }
          }
        });
      });

    return items;
  }, [friendRequests, activities, user.id, notifications]);

  // Merge with stored notifications
  const allNotifications = [...notifications, ...generatedNotifications]
    .filter((notification, index, self) => self.findIndex((n) => n.id === notification.id) === index)
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

  const unreadCount = allNotifications.filter((n) => !n.read).length;

  const handleMarkAsRead = (notificationId: string) => {
    setNotifications(
      allNotifications.map((n) => (n.id === notificationId ? { ...n, read: true } : n))
    );
  };

  const handleMarkAllAsRead = () => {
    setNotifications(allNotifications.map((n) => ({ ...n, read: true })));
  };

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'friend_request':
        return '👥';
      case 'like':
        return '❤️';
      case 'comment':
        return '💬';
      case 'badge':
        return '🏆';
      default:
        return '🔔';
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1>Notifications</h1>
          <p className="text-sm text-gray-600">
            {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
          </p>
        </div>
        {unreadCount > 0 && (
          <Button onClick={handleMarkAllAsRead} variant="outline" size="sm">
            <Check size={16} />
            <span className="ml-1">Mark all as read</span>
          </Button>
        )}
      </div>

      {allNotifications.length === 0 ? (
        <Card className="p-12 text-center">
          <div className="flex flex-col items-center gap-4">
            <div className="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center">
              <Bell size={40} className="text-gray-400" />
            </div>
            <div>
              <h3>No notifications</h3>
              <p className="text-sm text-gray-600 mt-1">You're all caught up!</p>
            </div>
          </div>
        </Card>
      ) : (
        <div className="space-y-2">
          {allNotifications.map((notification) => (
            <Card
              key={notification.id}
              className={notification.read ? 'opacity-60' : 'border-blue-200'}
            >
              <CardContent className="p-4">
                <div className="flex items-start gap-4">
                  <div className="text-2xl">{getNotificationIcon(notification.type)}</div>
                  <div className="flex-1">
                    <p className="text-sm">{notification.content}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(notification.createdAt).toLocaleDateString()}{' '}
                      {new Date(notification.createdAt).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {!notification.read && (
                      <>
                        <Badge variant="default" className="text-xs">
                          New
                        </Badge>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleMarkAsRead(notification.id)}
                        >
                          <Check size={16} />
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
