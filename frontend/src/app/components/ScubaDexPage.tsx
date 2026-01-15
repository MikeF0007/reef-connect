import React, { useState, useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLocalStorage } from '../hooks/useStorage';
import { SpeciesTag, Media, ScubaDexEntry } from '../types';
import { mockSpeciesCatalog } from '../data/mockSpecies';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Fish, Lock } from 'lucide-react';
import { Input } from './ui/input';

export function ScubaDexPage() {
  const { user } = useAuth();
  const [speciesTags] = useLocalStorage<SpeciesTag[]>('reefconnect_species_tags', []);
  const [media] = useLocalStorage<Media[]>('reefconnect_media', []);
  const [selectedEntry, setSelectedEntry] = useState<ScubaDexEntry | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  if (!user) return null;

  // Derive ScubaDex from species tags
  const scubaDex = useMemo(() => {
    const userTags = speciesTags.filter((tag) => tag.userId === user.id);
    const speciesMap = new Map<string, ScubaDexEntry>();

    userTags.forEach((tag) => {
      const species = mockSpeciesCatalog.find((s) => s.id === tag.speciesId);
      if (!species) return;

      if (speciesMap.has(tag.speciesId)) {
        const entry = speciesMap.get(tag.speciesId)!;
        entry.encounterCount += 1;
        if (!entry.mediaIds.includes(tag.mediaId)) {
          entry.mediaIds.push(tag.mediaId);
        }
      } else {
        speciesMap.set(tag.speciesId, {
          speciesId: tag.speciesId,
          species,
          firstSeenDate: tag.createdAt,
          encounterCount: 1,
          mediaIds: [tag.mediaId],
        });
      }
    });

    return Array.from(speciesMap.values()).sort((a, b) =>
      a.species.commonName.localeCompare(b.species.commonName)
    );
  }, [speciesTags, user.id]);

  // Get undiscovered species
  const discoveredIds = new Set(scubaDex.map((e) => e.speciesId));
  const undiscovered = mockSpeciesCatalog
    .filter((s) => !discoveredIds.has(s.id))
    .sort((a, b) => a.commonName.localeCompare(b.commonName));

  const filteredDiscovered = scubaDex.filter(
    (entry) =>
      entry.species.commonName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entry.species.scientificName.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredUndiscovered = undiscovered.filter(
    (species) =>
      species.commonName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      species.scientificName.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getEntryMedia = (entry: ScubaDexEntry) => {
    return media.filter((m) => entry.mediaIds.includes(m.id));
  };

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1>ScubaDex</h1>
          <p className="text-sm text-gray-600">
            {scubaDex.length} of {mockSpeciesCatalog.length} species discovered
          </p>
        </div>
      </div>

      <Input
        placeholder="Search species..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />

      <div>
        <h2 className="mb-4">Discovered Species</h2>
        {filteredDiscovered.length === 0 ? (
          <Card className="p-12 text-center">
            <div className="flex flex-col items-center gap-4">
              <div className="w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center">
                <Fish size={40} className="text-blue-600" />
              </div>
              <div>
                <h3>No species discovered yet</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Tag species in your dive photos to build your ScubaDex
                </p>
              </div>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {filteredDiscovered.map((entry) => (
              <Card
                key={entry.speciesId}
                className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => setSelectedEntry(entry)}
              >
                <CardContent className="p-4">
                  {entry.species.imageUrl ? (
                    <img
                      src={entry.species.imageUrl}
                      alt={entry.species.commonName}
                      className="w-full aspect-square object-cover rounded-lg mb-2"
                    />
                  ) : (
                    <div className="w-full aspect-square bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg mb-2 flex items-center justify-center">
                      <Fish size={40} className="text-white opacity-50" />
                    </div>
                  )}
                  <h3 className="text-sm">{entry.species.commonName}</h3>
                  <p className="text-xs text-gray-500 italic">{entry.species.scientificName}</p>
                  <div className="flex gap-2 mt-2">
                    <Badge variant="secondary" className="text-xs">
                      {entry.encounterCount} encounters
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      <div>
        <h2 className="mb-4">Undiscovered Species</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredUndiscovered.map((species) => (
            <Card key={species.id} className="opacity-50">
              <CardContent className="p-4">
                <div className="w-full aspect-square bg-gray-200 rounded-lg mb-2 flex items-center justify-center relative">
                  <Lock size={40} className="text-gray-400" />
                </div>
                <h3 className="text-sm text-gray-500">???</h3>
                <p className="text-xs text-gray-400">{species.category}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Entry Detail Dialog */}
      <Dialog open={!!selectedEntry} onOpenChange={() => setSelectedEntry(null)}>
        <DialogContent className="max-w-3xl">
          {selectedEntry && (
            <>
              <DialogHeader>
                <DialogTitle>{selectedEntry.species.commonName}</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-500">Scientific Name</p>
                  <p className="italic">{selectedEntry.species.scientificName}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Category</p>
                  <p>{selectedEntry.species.category}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">First Seen</p>
                  <p>{new Date(selectedEntry.firstSeenDate).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Total Encounters</p>
                  <p>{selectedEntry.encounterCount}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-2">Your Photos</p>
                  <div className="grid grid-cols-3 gap-2">
                    {getEntryMedia(selectedEntry).map((mediaItem) => (
                      <img
                        key={mediaItem.id}
                        src={mediaItem.thumbnailUrl}
                        alt="Species photo"
                        className="w-full aspect-square object-cover rounded-lg"
                      />
                    ))}
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
