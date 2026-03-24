import React, { useEffect, useState } from 'react';
import {
  getMyCertifications,
  addMyCertification,
  updateMyCertification,
  deleteMyCertification,
  type UserCertification,
  type UserCertificationCreate,
} from '../../api/certificationApi';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Edit, Save, X, Award } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';

export function ProfilePage() {
  const { user, updateProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    username: user?.username || '',
    bio: user?.bio || '',
  });
  const [certifications, setCertifications] = useState<UserCertification[]>([]);
  const [newCertForm, setNewCertForm] = useState<UserCertificationCreate>({
    certification_name: '',
    issuer: '',
    issued_date: '',
  });
  const [editingCertId, setEditingCertId] = useState<string | null>(null);
  const [editCertForm, setEditCertForm] = useState<UserCertificationCreate>({
    certification_name: '',
    issuer: '',
    issued_date: '',
  });

  useEffect(() => {
    getMyCertifications().then(setCertifications).catch(console.error);
  }, []);

  if (!user) return null;

  const handleSave = async () => {
    await updateProfile(formData);
    setIsEditing(false);
  };

  const handleAddCertification = async () => {
    const { certification_name, issuer, issued_date } = newCertForm;
    if (!certification_name.trim() || !issuer.trim() || !issued_date) return;
    const created = await addMyCertification(newCertForm);
    setCertifications((prev) => [...prev, created]);
    setNewCertForm({ certification_name: '', issuer: '', issued_date: '' });
  };

  const handleRemoveCertification = async (id: string) => {
    await deleteMyCertification(id);
    setCertifications((prev) => prev.filter((c) => c.id !== id));
  };

  const handleEditCertification = (cert: UserCertification) => {
    setEditingCertId(cert.id);
    setEditCertForm({
      certification_name: cert.certification_name,
      issuer: cert.issuer,
      issued_date: cert.issued_date,
    });
  };

  const handleSaveEditCertification = async () => {
    if (!editingCertId) return;
    const updated = await updateMyCertification(editingCertId, editCertForm);
    setCertifications((prev) =>
      prev.map((c) => (c.id === editingCertId ? updated : c)),
    );
    setEditingCertId(null);
  };

  const handleCancelEdit = () => {
    setEditingCertId(null);
  };

  return (
    <div className='max-w-4xl mx-auto p-4 space-y-6'>
      <Card>
        <CardHeader className='flex flex-row items-center justify-between'>
          <CardTitle>Profile</CardTitle>
          {!isEditing ? (
            <Button onClick={() => setIsEditing(true)} size='sm'>
              <Edit size={16} />
              <span className='ml-1'>Edit</span>
            </Button>
          ) : (
            <div className='flex gap-2'>
              <Button onClick={handleSave} size='sm'>
                <Save size={16} />
                <span className='ml-1'>Save</span>
              </Button>
              <Button
                onClick={() => {
                  setIsEditing(false);
                  setFormData({
                    username: user.username,
                    bio: user.bio || '',
                  });
                }}
                variant='outline'
                size='sm'
              >
                <X size={16} />
                <span className='ml-1'>Cancel</span>
              </Button>
            </div>
          )}
        </CardHeader>
        <CardContent className='space-y-4'>
          <div className='flex items-center gap-4'>
            <div className='w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center'>
              <span className='text-3xl'>{user.username[0].toUpperCase()}</span>
            </div>
            <div className='flex-1'>
              {isEditing ? (
                <div className='space-y-2'>
                  <Label htmlFor='username'>Username</Label>
                  <Input
                    id='username'
                    value={formData.username}
                    onChange={(e) =>
                      setFormData({ ...formData, username: e.target.value })
                    }
                  />
                </div>
              ) : (
                <div>
                  <p className='text-sm text-gray-500'>Username</p>
                  <p>{user.username}</p>
                </div>
              )}
            </div>
          </div>

          <div>
            <Label>Email</Label>
            <p className='text-sm text-gray-600'>{user.email}</p>
          </div>

          <div>
            <Label htmlFor='bio'>Bio</Label>
            {isEditing ? (
              <Textarea
                id='bio'
                value={formData.bio}
                onChange={(e) =>
                  setFormData({ ...formData, bio: e.target.value })
                }
                placeholder='Tell us about your diving experience...'
                className='mt-1'
              />
            ) : (
              <p className='text-sm text-gray-600 mt-1'>
                {user.bio || 'No bio added yet'}
              </p>
            )}
          </div>

          <div>
            <Label>Certifications</Label>
            {isEditing ? (
              <div className='space-y-2 mt-2'>
                <div className='grid grid-cols-3 gap-2'>
                  <Input
                    value={newCertForm.certification_name}
                    onChange={(e) =>
                      setNewCertForm({
                        ...newCertForm,
                        certification_name: e.target.value,
                      })
                    }
                    placeholder='Certification name'
                  />
                  <Input
                    value={newCertForm.issuer}
                    onChange={(e) =>
                      setNewCertForm({ ...newCertForm, issuer: e.target.value })
                    }
                    placeholder='Issuer (e.g. PADI)'
                  />
                  <div className='flex gap-2'>
                    <Input
                      type='date'
                      value={newCertForm.issued_date}
                      onChange={(e) =>
                        setNewCertForm({
                          ...newCertForm,
                          issued_date: e.target.value,
                        })
                      }
                    />
                    <Button onClick={handleAddCertification} size='sm'>
                      Add
                    </Button>
                  </div>
                </div>
                <div className='flex flex-wrap gap-2'>
                  {certifications.map((cert) =>
                    editingCertId === cert.id ? (
                      <div
                        key={cert.id}
                        className='flex items-center gap-2 p-2 border rounded-md bg-gray-50'
                      >
                        <Input
                          value={editCertForm.certification_name}
                          onChange={(e) =>
                            setEditCertForm({
                              ...editCertForm,
                              certification_name: e.target.value,
                            })
                          }
                          placeholder='Name'
                          className='w-32'
                        />
                        <Input
                          value={editCertForm.issuer}
                          onChange={(e) =>
                            setEditCertForm({
                              ...editCertForm,
                              issuer: e.target.value,
                            })
                          }
                          placeholder='Issuer'
                          className='w-20'
                        />
                        <Input
                          type='date'
                          value={editCertForm.issued_date}
                          onChange={(e) =>
                            setEditCertForm({
                              ...editCertForm,
                              issued_date: e.target.value,
                            })
                          }
                          className='w-32'
                        />
                        <Button
                          onClick={handleSaveEditCertification}
                          size='sm'
                          variant='outline'
                        >
                          Save
                        </Button>
                        <Button
                          onClick={handleCancelEdit}
                          size='sm'
                          variant='ghost'
                        >
                          Cancel
                        </Button>
                      </div>
                    ) : (
                      <Badge
                        key={cert.id}
                        variant='secondary'
                        className='gap-1'
                      >
                        <Award size={14} />
                        {cert.certification_name}
                        <button
                          onClick={() => handleEditCertification(cert)}
                          className='ml-1 hover:text-blue-600'
                          title='Edit certification'
                        >
                          <Edit size={14} />
                        </button>
                        <button
                          onClick={() => handleRemoveCertification(cert.id)}
                          className='ml-1 hover:text-red-600'
                        >
                          <X size={14} />
                        </button>
                      </Badge>
                    ),
                  )}
                </div>
              </div>
            ) : (
              <div className='flex flex-wrap gap-2 mt-2'>
                {certifications.length > 0 ? (
                  certifications.map((cert) => (
                    <Badge key={cert.id} variant='secondary'>
                      <Award size={14} />
                      <span className='ml-1'>{cert.certification_name}</span>
                    </Badge>
                  ))
                ) : (
                  <p className='text-sm text-gray-500'>
                    No certifications added
                  </p>
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
          <CardContent className='space-y-4'>
            <div className='space-y-2'>
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
                  <SelectItem value='public'>Public</SelectItem>
                  <SelectItem value='friends'>Friends Only</SelectItem>
                  <SelectItem value='private'>Private</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className='space-y-2'>
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
                  <SelectItem value='public'>Public</SelectItem>
                  <SelectItem value='friends'>Friends Only</SelectItem>
                  <SelectItem value='private'>Private</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
