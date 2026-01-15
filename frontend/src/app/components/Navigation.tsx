import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/button';
import { Waves, User, Book, Users, Activity, BarChart3, Trophy, Bell } from 'lucide-react';
import { Badge } from './ui/badge';

interface NavigationProps {
  currentPage: string;
  onNavigate: (page: string) => void;
  notificationCount?: number;
}

export function Navigation({ currentPage, onNavigate, notificationCount = 0 }: NavigationProps) {
  const { user, logout } = useAuth();

  const navItems = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'dives', label: 'Dive Logs', icon: Book },
    { id: 'scubadex', label: 'ScubaDex', icon: Activity },
    { id: 'friends', label: 'Friends', icon: Users },
    { id: 'feed', label: 'Feed', icon: Activity },
    { id: 'stats', label: 'Stats', icon: BarChart3 },
    { id: 'leaderboard', label: 'Leaderboard', icon: Trophy },
  ];

  return (
    <nav className="bg-white border-b sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <div className="bg-blue-600 text-white p-2 rounded-lg">
              <Waves size={24} />
            </div>
            <span className="font-semibold">ReefConnect</span>
          </div>
          
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Button
                  key={item.id}
                  variant={currentPage === item.id ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => onNavigate(item.id)}
                >
                  <Icon size={16} />
                  <span className="ml-1">{item.label}</span>
                </Button>
              );
            })}
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onNavigate('notifications')}
              className="relative"
            >
              <Bell size={20} />
              {notificationCount > 0 && (
                <Badge className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs">
                  {notificationCount}
                </Badge>
              )}
            </Button>
            <span className="text-sm text-gray-600 hidden sm:inline">
              {user?.username}
            </span>
            <Button variant="outline" size="sm" onClick={logout}>
              Logout
            </Button>
          </div>
        </div>

        {/* Mobile navigation */}
        <div className="md:hidden pb-2 flex gap-1 overflow-x-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Button
                key={item.id}
                variant={currentPage === item.id ? 'default' : 'ghost'}
                size="sm"
                onClick={() => onNavigate(item.id)}
                className="flex-shrink-0"
              >
                <Icon size={16} />
              </Button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
