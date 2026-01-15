import React, { useState } from 'react';
import { DiveLog } from '../types';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

interface DiveLogFormProps {
  dive?: DiveLog;
  onSave: (dive: Omit<DiveLog, 'id' | 'userId' | 'createdAt' | 'updatedAt'>) => void;
  onCancel: () => void;
}

export function DiveLogForm({ dive, onSave, onCancel }: DiveLogFormProps) {
  const [formData, setFormData] = useState({
    date: dive?.date || new Date().toISOString().split('T')[0],
    time: dive?.time || '12:00',
    location: dive?.location || '',
    site: dive?.site || '',
    depth: dive?.depth || 0,
    duration: dive?.duration || 0,
    waterTemp: dive?.waterTemp || undefined,
    airTemp: dive?.airTemp || undefined,
    visibility: dive?.visibility || undefined,
    conditions: dive?.conditions || '',
    notes: dive?.notes || '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({
      ...formData,
      waterTemp: formData.waterTemp ? Number(formData.waterTemp) : undefined,
      airTemp: formData.airTemp ? Number(formData.airTemp) : undefined,
      visibility: formData.visibility ? Number(formData.visibility) : undefined,
    });
  };

  return (
    <div className="max-w-3xl mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>{dive ? 'Edit Dive Log' : 'New Dive Log'}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="date">Date *</Label>
                <Input
                  id="date"
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="time">Time</Label>
                <Input
                  id="time"
                  type="time"
                  value={formData.time}
                  onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="location">Location *</Label>
              <Input
                id="location"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                placeholder="e.g., Great Barrier Reef"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="site">Dive Site</Label>
              <Input
                id="site"
                value={formData.site}
                onChange={(e) => setFormData({ ...formData, site: e.target.value })}
                placeholder="e.g., Cod Hole"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="depth">Max Depth (meters) *</Label>
                <Input
                  id="depth"
                  type="number"
                  step="0.1"
                  value={formData.depth}
                  onChange={(e) => setFormData({ ...formData, depth: Number(e.target.value) })}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="duration">Duration (minutes) *</Label>
                <Input
                  id="duration"
                  type="number"
                  value={formData.duration}
                  onChange={(e) => setFormData({ ...formData, duration: Number(e.target.value) })}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="waterTemp">Water Temp (°C)</Label>
                <Input
                  id="waterTemp"
                  type="number"
                  step="0.1"
                  value={formData.waterTemp || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, waterTemp: e.target.value ? Number(e.target.value) : undefined })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="airTemp">Air Temp (°C)</Label>
                <Input
                  id="airTemp"
                  type="number"
                  step="0.1"
                  value={formData.airTemp || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, airTemp: e.target.value ? Number(e.target.value) : undefined })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="visibility">Visibility (meters)</Label>
                <Input
                  id="visibility"
                  type="number"
                  step="0.1"
                  value={formData.visibility || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, visibility: e.target.value ? Number(e.target.value) : undefined })
                  }
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="conditions">Conditions</Label>
              <Input
                id="conditions"
                value={formData.conditions}
                onChange={(e) => setFormData({ ...formData, conditions: e.target.value })}
                placeholder="e.g., Calm seas, slight current"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Notes</Label>
              <Textarea
                id="notes"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                placeholder="Write about your dive experience..."
                rows={4}
              />
            </div>

            <div className="flex gap-2">
              <Button type="submit">{dive ? 'Update' : 'Create'} Dive Log</Button>
              <Button type="button" variant="outline" onClick={onCancel}>
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
