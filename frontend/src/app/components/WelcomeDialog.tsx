import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Button } from './ui/button';
import { Book, Fish, Users, Trophy, Waves } from 'lucide-react';

export function WelcomeDialog() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const hasSeenWelcome = localStorage.getItem('reefconnect_welcome_seen');
    if (!hasSeenWelcome) {
      setOpen(true);
    }
  }, []);

  const handleClose = () => {
    localStorage.setItem('reefconnect_welcome_seen', 'true');
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <div className="flex items-center justify-center mb-4">
            <div className="bg-blue-600 text-white p-4 rounded-full">
              <Waves size={32} />
            </div>
          </div>
          <DialogTitle className="text-center">Welcome to ReefConnect!</DialogTitle>
          <DialogDescription className="text-center">
            Your personal dive log and social platform for scuba divers
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 my-4">
          <div className="flex gap-3">
            <div className="bg-blue-100 p-2 rounded-lg h-fit">
              <Book className="text-blue-600" size={24} />
            </div>
            <div>
              <h3 className="text-sm mb-1">Log Your Dives</h3>
              <p className="text-sm text-gray-600">
                Record dive details including location, depth, duration, and conditions
              </p>
            </div>
          </div>

          <div className="flex gap-3">
            <div className="bg-green-100 p-2 rounded-lg h-fit">
              <Fish className="text-green-600" size={24} />
            </div>
            <div>
              <h3 className="text-sm mb-1">Build Your ScubaDex</h3>
              <p className="text-sm text-gray-600">
                Tag species in your photos and automatically build a collection of marine life you've encountered
              </p>
            </div>
          </div>

          <div className="flex gap-3">
            <div className="bg-purple-100 p-2 rounded-lg h-fit">
              <Users className="text-purple-600" size={24} />
            </div>
            <div>
              <h3 className="text-sm mb-1">Connect with Divers</h3>
              <p className="text-sm text-gray-600">
                Add friends, view their profiles, and share your diving adventures
              </p>
            </div>
          </div>

          <div className="flex gap-3">
            <div className="bg-yellow-100 p-2 rounded-lg h-fit">
              <Trophy className="text-yellow-600" size={24} />
            </div>
            <div>
              <h3 className="text-sm mb-1">Earn Achievements</h3>
              <p className="text-sm text-gray-600">
                Unlock badges, compete on leaderboards, and track your diving statistics
              </p>
            </div>
          </div>
        </div>

        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm">
            <strong>Demo Account:</strong> You can use the demo account to explore the app
          </p>
          <p className="text-sm mt-1">
            Email: <code className="bg-white px-1 rounded">demo@reefconnect.com</code>
          </p>
          <p className="text-sm">
            Password: <code className="bg-white px-1 rounded">demo</code>
          </p>
        </div>

        <Button onClick={handleClose} className="w-full">
          Get Started
        </Button>
      </DialogContent>
    </Dialog>
  );
}
