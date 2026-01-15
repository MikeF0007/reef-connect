import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Edit, Save, X, Award } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';

export function ProfilePage() {
  const { user, updateProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    username: user?.username || '',
    bio: user?.bio || '',
    certifications: user?.certifications || [],
  });
  const [newCert, setNewCert] = useState('');

  if (!user) return null;

  const handleSave = () => {
    updateProfile(formData);
    setIsEditing(false);
  };

  const handleAddCertification = () => {
    if (newCert.trim()) {
      setFormData({
        ...formData,
        certifications: [...formData.certifications, newCert.trim()],
      });
      setNewCert('');
    }
  };

  const handleRemoveCertification = (index: number) => {
    setFormData({
      ...formData,
      certifications: formData.certifications.filter((_, i) => i !== index),
    });
  };

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Profile</CardTitle>
          {!isEditing ? (
            <Button onClick={() => setIsEditing(true)} size="sm">
              <Edit size={16} />
              <span className="ml-1">Edit</span>
            </Button>
          ) : (
            <div className="flex gap-2">
              <Button onClick={handleSave} size="sm">
                <Save size={16} />
                <span className="ml-1">Save</span>
              </Button>
              <Button
                onClick={() => {
                  setIsEditing(false);
                  setFormData({
                    username: user.username,
                    bio: user.bio || '',
                    certifications: user.certifications,
                  });
                }}
                variant="outline"
                size="sm"
              >
                <X size={16} />
                <span className="ml-1">Cancel</span>
              </Button>
            </div>
          )}
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center">
              <span className="text-3xl">{user.username[0].toUpperCase()}</span>
            </div>
            <div className="flex-1">
              {isEditing ? (
                <div className="space-y-2">
                  <Label htmlFor="username">Username</Label>
                  <Input
                    id="username"
                    value={formData.username}
                    onChange={(e) =>
                      setFormData({ ...formData, username: e.target.value })
                    }
                  />
                </div>
              ) : (
                <div>
                  <p className="text-sm text-gray-500">Username</p>
                  <p>{user.username}</p>
                </div>
              )}
            </div>
          </div>

          <div>
            <Label>Email</Label>
            <p className="text-sm text-gray-600">{user.email}</p>
          </div>

          <div>
            <Label htmlFor="bio">Bio</Label>
            {isEditing ? (
              <Textarea
                id="bio"
                value={formData.bio}
                onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                placeholder="Tell us about your diving experience..."
                className="mt-1"
              />
            ) : (
              <p className="text-sm text-gray-600 mt-1">
                {user.bio || 'No bio added yet'}
              </p>
            )}
          </div>

          <div>
            <Label>Certifications</Label>
            {isEditing ? (
              <div className="space-y-2 mt-2">
                <div className="flex gap-2">
                  <Input
                    value={newCert}
                    onChange={(e) => setNewCert(e.target.value)}
                    placeholder="Add certification..."
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleAddCertification();
                      }
                    }}
                  />
                  <Button onClick={handleAddCertification} size="sm">
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.certifications.map((cert, index) => (
                    <Badge key={index} variant="secondary" className="gap-1">
                      <Award size={14} />
                      {cert}
                      <button
                        onClick={() => handleRemoveCertification(index)}
                        className="ml-1 hover:text-red-600"
                      >
                        <X size={14} />
                      </button>
                    </Badge>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex flex-wrap gap-2 mt-2">
                {user.certifications.length > 0 ? (
                  user.certifications.map((cert, index) => (
                    <Badge key={index} variant="secondary">
                      <Award size={14} />
                      <span className="ml-1">{cert}</span>
                    </Badge>
                  ))
                ) : (
                  <p className="text-sm text-gray-500">No certifications added</p>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {isEditing && (
        <Card>
          <CardHeader>
            <CardTitle>Privacy Settings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Profile Visibility</Label>
              <Select
                value={user.privacySettings.profileVisibility}
                onValueChange={(value) =>
                  updateProfile({
                    privacySettings: {
                      ...user.privacySettings,
                      profileVisibility: value as any,
                    },
                  })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="public">Public</SelectItem>
                  <SelectItem value="friends">Friends Only</SelectItem>
                  <SelectItem value="private">Private</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Dive Logs Visibility</Label>
              <Select
                value={user.privacySettings.diveLogsVisibility}
                onValueChange={(value) =>
                  updateProfile({
                    privacySettings: {
                      ...user.privacySettings,
                      diveLogsVisibility: value as any,
                    },
                  })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="public">Public</SelectItem>
                  <SelectItem value="friends">Friends Only</SelectItem>
                  <SelectItem value="private">Private</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
