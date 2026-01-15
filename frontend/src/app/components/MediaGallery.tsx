import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLocalStorage } from '../hooks/useStorage';
import { Media, SpeciesTag, Species } from '../types';
import { mockSpeciesCatalog } from '../data/mockSpecies';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Upload, X, Tag, Trash2 } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';

interface MediaGalleryProps {
  diveLogId: string;
}

export function MediaGallery({ diveLogId }: MediaGalleryProps) {
  const { user } = useAuth();
  const [media, setMedia] = useLocalStorage<Media[]>('reefconnect_media', []);
  const [speciesTags, setSpeciesTags] = useLocalStorage<SpeciesTag[]>('reefconnect_species_tags', []);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [selectedMedia, setSelectedMedia] = useState<Media | null>(null);
  const [uploadUrl, setUploadUrl] = useState('');
  const [uploadCaption, setUploadCaption] = useState('');
  const [selectedSpecies, setSelectedSpecies] = useState<string>('');

  if (!user) return null;

  const diveMedia = media.filter((m) => m.diveLogId === diveLogId);

  const handleUpload = () => {
    if (!uploadUrl.trim()) return;

    const newMedia: Media = {
      id: crypto.randomUUID(),
      userId: user.id,
      diveLogId,
      type: 'photo',
      url: uploadUrl,
      thumbnailUrl: uploadUrl,
      caption: uploadCaption,
      uploadedAt: new Date().toISOString(),
    };

    setMedia([...media, newMedia]);
    setUploadUrl('');
    setUploadCaption('');
    setIsUploadOpen(false);
  };

  const handleDelete = (mediaId: string) => {
    if (confirm('Delete this photo? This will also remove any species tags.')) {
      setMedia(media.filter((m) => m.id !== mediaId));
      setSpeciesTags(speciesTags.filter((t) => t.mediaId !== mediaId));
      setSelectedMedia(null);
    }
  };

  const handleAddSpeciesTag = () => {
    if (!selectedMedia || !selectedSpecies) return;

    // Check if already tagged
    const existingTag = speciesTags.find(
      (t) => t.mediaId === selectedMedia.id && t.speciesId === selectedSpecies
    );
    if (existingTag) return;

    const newTag: SpeciesTag = {
      id: crypto.randomUUID(),
      mediaId: selectedMedia.id,
      speciesId: selectedSpecies,
      userId: user.id,
      createdAt: new Date().toISOString(),
    };

    setSpeciesTags([...speciesTags, newTag]);
    setSelectedSpecies('');
  };

  const handleRemoveSpeciesTag = (tagId: string) => {
    setSpeciesTags(speciesTags.filter((t) => t.id !== tagId));
  };

  const getMediaTags = (mediaId: string) => {
    return speciesTags.filter((t) => t.mediaId === mediaId);
  };

  const getSpecies = (speciesId: string): Species | undefined => {
    return mockSpeciesCatalog.find((s) => s.id === speciesId);
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Photos & Media</CardTitle>
          <Button size="sm" onClick={() => setIsUploadOpen(true)}>
            <Upload size={16} />
            <span className="ml-1">Upload</span>
          </Button>
        </CardHeader>
        <CardContent>
          {diveMedia.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Upload size={40} className="mx-auto mb-2 opacity-50" />
              <p>No media uploaded yet</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {diveMedia.map((item) => {
                const tags = getMediaTags(item.id);
                return (
                  <div
                    key={item.id}
                    className="group relative cursor-pointer"
                    onClick={() => setSelectedMedia(item)}
                  >
                    <img
                      src={item.thumbnailUrl}
                      alt={item.caption || 'Dive photo'}
                      className="w-full aspect-square object-cover rounded-lg"
                    />
                    {tags.length > 0 && (
                      <Badge className="absolute top-2 right-2" variant="secondary">
                        <Tag size={12} />
                        <span className="ml-1">{tags.length}</span>
                      </Badge>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upload Dialog */}
      <Dialog open={isUploadOpen} onOpenChange={setIsUploadOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upload Media</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="url">Image URL</Label>
              <Input
                id="url"
                value={uploadUrl}
                onChange={(e) => setUploadUrl(e.target.value)}
                placeholder="https://example.com/image.jpg"
              />
              <p className="text-xs text-gray-500">
                In a production app, this would be a file upload
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="caption">Caption (optional)</Label>
              <Input
                id="caption"
                value={uploadCaption}
                onChange={(e) => setUploadCaption(e.target.value)}
                placeholder="Describe your photo..."
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleUpload} disabled={!uploadUrl.trim()}>
                Upload
              </Button>
              <Button variant="outline" onClick={() => setIsUploadOpen(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Media Detail Dialog */}
      <Dialog open={!!selectedMedia} onOpenChange={() => setSelectedMedia(null)}>
        <DialogContent className="max-w-3xl">
          {selectedMedia && (
            <>
              <DialogHeader>
                <DialogTitle>Media Details</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <img
                  src={selectedMedia.url}
                  alt={selectedMedia.caption || 'Dive photo'}
                  className="w-full rounded-lg"
                />
                {selectedMedia.caption && (
                  <p className="text-sm text-gray-600">{selectedMedia.caption}</p>
                )}

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label>Species Tags</Label>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(selectedMedia.id)}
                    >
                      <Trash2 size={14} />
                      <span className="ml-1">Delete Photo</span>
                    </Button>
                  </div>

                  <div className="flex gap-2">
                    <Select value={selectedSpecies} onValueChange={setSelectedSpecies}>
                      <SelectTrigger className="flex-1">
                        <SelectValue placeholder="Select species..." />
                      </SelectTrigger>
                      <SelectContent>
                        {mockSpeciesCatalog.map((species) => (
                          <SelectItem key={species.id} value={species.id}>
                            {species.commonName} ({species.scientificName})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Button onClick={handleAddSpeciesTag} disabled={!selectedSpecies}>
                      <Tag size={16} />
                      <span className="ml-1">Add</span>
                    </Button>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {getMediaTags(selectedMedia.id).map((tag) => {
                      const species = getSpecies(tag.speciesId);
                      if (!species) return null;
                      return (
                        <Badge key={tag.id} variant="secondary" className="gap-1">
                          {species.commonName}
                          <button
                            onClick={() => handleRemoveSpeciesTag(tag.id)}
                            className="ml-1 hover:text-red-600"
                          >
                            <X size={14} />
                          </button>
                        </Badge>
                      );
                    })}
                  </div>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
