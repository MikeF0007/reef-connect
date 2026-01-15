import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLocalStorage } from '../hooks/useStorage';
import { DiveLog, Media, SpeciesTag } from '../types';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Plus, MapPin, Gauge, Clock, Thermometer, Eye, Calendar, Edit, Trash2, Image as ImageIcon } from 'lucide-react';
import { DiveLogForm } from './DiveLogForm';
import { MediaGallery } from './MediaGallery';

export function DiveLogPage() {
  const { user } = useAuth();
  const [diveLogs, setDiveLogs] = useLocalStorage<DiveLog[]>('reefconnect_dives', []);
  const [media] = useLocalStorage<Media[]>('reefconnect_media', []);
  const [selectedDive, setSelectedDive] = useState<DiveLog | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingDive, setEditingDive] = useState<DiveLog | null>(null);
  const [sortBy, setSortBy] = useState<'date' | 'depth'>('date');

  if (!user) return null;

  const userDives = diveLogs
    .filter((dive) => dive.userId === user.id)
    .sort((a, b) => {
      if (sortBy === 'date') {
        return new Date(b.date).getTime() - new Date(a.date).getTime();
      }
      return b.depth - a.depth;
    });

  const handleCreateDive = (dive: Omit<DiveLog, 'id' | 'userId' | 'createdAt' | 'updatedAt'>) => {
    const newDive: DiveLog = {
      ...dive,
      id: crypto.randomUUID(),
      userId: user.id,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setDiveLogs([...diveLogs, newDive]);
    setIsFormOpen(false);
  };

  const handleUpdateDive = (dive: Omit<DiveLog, 'id' | 'userId' | 'createdAt' | 'updatedAt'>) => {
    if (!editingDive) return;
    
    const updatedDive: DiveLog = {
      ...editingDive,
      ...dive,
      updatedAt: new Date().toISOString(),
    };
    setDiveLogs(diveLogs.map((d) => (d.id === editingDive.id ? updatedDive : d)));
    setEditingDive(null);
    setIsFormOpen(false);
  };

  const handleDeleteDive = (diveId: string) => {
    if (confirm('Are you sure you want to delete this dive log?')) {
      setDiveLogs(diveLogs.filter((d) => d.id !== diveId));
      setSelectedDive(null);
    }
  };

  const getDiveMedia = (diveId: string) => {
    return media.filter((m) => m.diveLogId === diveId);
  };

  if (isFormOpen) {
    return (
      <DiveLogForm
        dive={editingDive || undefined}
        onSave={editingDive ? handleUpdateDive : handleCreateDive}
        onCancel={() => {
          setIsFormOpen(false);
          setEditingDive(null);
        }}
      />
    );
  }

  if (selectedDive) {
    const diveMedia = getDiveMedia(selectedDive.id);
    
    return (
      <div className="max-w-4xl mx-auto p-4 space-y-6">
        <div className="flex items-center justify-between">
          <Button variant="outline" onClick={() => setSelectedDive(null)}>
            Back to List
          </Button>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setEditingDive(selectedDive);
                setIsFormOpen(true);
              }}
            >
              <Edit size={16} />
              <span className="ml-1">Edit</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleDeleteDive(selectedDive.id)}
            >
              <Trash2 size={16} />
              <span className="ml-1">Delete</span>
            </Button>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>{selectedDive.location}</CardTitle>
            {selectedDive.site && <p className="text-sm text-gray-600">{selectedDive.site}</p>}
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="flex items-center gap-2">
                <Calendar className="text-blue-600" size={20} />
                <div>
                  <p className="text-xs text-gray-500">Date</p>
                  <p className="text-sm">{new Date(selectedDive.date).toLocaleDateString()}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="text-blue-600" size={20} />
                <div>
                  <p className="text-xs text-gray-500">Duration</p>
                  <p className="text-sm">{selectedDive.duration} min</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Gauge className="text-blue-600" size={20} />
                <div>
                  <p className="text-xs text-gray-500">Max Depth</p>
                  <p className="text-sm">{selectedDive.depth} m</p>
                </div>
              </div>
              {selectedDive.waterTemp && (
                <div className="flex items-center gap-2">
                  <Thermometer className="text-blue-600" size={20} />
                  <div>
                    <p className="text-xs text-gray-500">Water Temp</p>
                    <p className="text-sm">{selectedDive.waterTemp}°C</p>
                  </div>
                </div>
              )}
              {selectedDive.visibility && (
                <div className="flex items-center gap-2">
                  <Eye className="text-blue-600" size={20} />
                  <div>
                    <p className="text-xs text-gray-500">Visibility</p>
                    <p className="text-sm">{selectedDive.visibility} m</p>
                  </div>
                </div>
              )}
            </div>

            {selectedDive.conditions && (
              <div>
                <p className="text-sm text-gray-500">Conditions</p>
                <p className="text-sm">{selectedDive.conditions}</p>
              </div>
            )}

            {selectedDive.notes && (
              <div>
                <p className="text-sm text-gray-500">Notes</p>
                <p className="text-sm">{selectedDive.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <MediaGallery diveLogId={selectedDive.id} />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1>Dive Logs</h1>
          <p className="text-sm text-gray-600">{userDives.length} total dives</p>
        </div>
        <Button onClick={() => setIsFormOpen(true)}>
          <Plus size={16} />
          <span className="ml-1">New Dive Log</span>
        </Button>
      </div>

      <div className="flex gap-2">
        <Button
          variant={sortBy === 'date' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setSortBy('date')}
        >
          Sort by Date
        </Button>
        <Button
          variant={sortBy === 'depth' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setSortBy('depth')}
        >
          Sort by Depth
        </Button>
      </div>

      {userDives.length === 0 ? (
        <Card className="p-12 text-center">
          <div className="flex flex-col items-center gap-4">
            <div className="w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center">
              <Plus size={40} className="text-blue-600" />
            </div>
            <div>
              <h3>No dive logs yet</h3>
              <p className="text-sm text-gray-600 mt-1">
                Start logging your dives to track your underwater adventures
              </p>
            </div>
            <Button onClick={() => setIsFormOpen(true)}>
              <Plus size={16} />
              <span className="ml-1">Create Your First Dive</span>
            </Button>
          </div>
        </Card>
      ) : (
        <div className="grid gap-4">
          {userDives.map((dive) => {
            const diveMedia = getDiveMedia(dive.id);
            return (
              <Card
                key={dive.id}
                className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => setSelectedDive(dive)}
              >
                <CardContent className="p-4">
                  <div className="flex gap-4">
                    {diveMedia.length > 0 ? (
                      <img
                        src={diveMedia[0].thumbnailUrl}
                        alt="Dive"
                        className="w-32 h-32 object-cover rounded-lg"
                      />
                    ) : (
                      <div className="w-32 h-32 bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg flex items-center justify-center">
                        <ImageIcon size={40} className="text-white opacity-50" />
                      </div>
                    )}
                    <div className="flex-1 space-y-2">
                      <div>
                        <h3>{dive.location}</h3>
                        {dive.site && <p className="text-sm text-gray-600">{dive.site}</p>}
                      </div>
                      <div className="flex flex-wrap gap-3 text-sm">
                        <Badge variant="secondary">
                          <Calendar size={14} />
                          <span className="ml-1">{new Date(dive.date).toLocaleDateString()}</span>
                        </Badge>
                        <Badge variant="secondary">
                          <Gauge size={14} />
                          <span className="ml-1">{dive.depth}m</span>
                        </Badge>
                        <Badge variant="secondary">
                          <Clock size={14} />
                          <span className="ml-1">{dive.duration} min</span>
                        </Badge>
                        {diveMedia.length > 0 && (
                          <Badge variant="secondary">
                            <ImageIcon size={14} />
                            <span className="ml-1">{diveMedia.length} photos</span>
                          </Badge>
                        )}
                      </div>
                    </div>
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
