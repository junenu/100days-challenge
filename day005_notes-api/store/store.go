// Package store provides thread-safe JSON file persistence for notes.
package store

import (
	"encoding/json"
	"errors"
	"os"
	"strings"
	"sync"
	"time"
)

// Note represents a single note entry.
type Note struct {
	ID        int      `json:"id"`
	Title     string   `json:"title"`
	Body      string   `json:"body"`
	Tags      []string `json:"tags"`
	CreatedAt string   `json:"created_at"`
	UpdatedAt string   `json:"updated_at"`
}

// ErrNotFound is returned when a note does not exist.
var ErrNotFound = errors.New("note not found")

// Store holds notes in memory and persists them to a JSON file.
type Store struct {
	mu       sync.RWMutex
	notes    []Note
	nextID   int
	dataFile string
}

// New creates a Store backed by dataFile.
func New(dataFile string) *Store {
	return &Store{dataFile: dataFile, nextID: 1}
}

// ── persistence ──────────────────────────────────────────────────────────────

type fileData struct {
	NextID int    `json:"next_id"`
	Notes  []Note `json:"notes"`
}

// Load reads notes from the data file. Missing file is treated as empty.
func (s *Store) Load() error {
	s.mu.Lock()
	defer s.mu.Unlock()

	data, err := os.ReadFile(s.dataFile)
	if errors.Is(err, os.ErrNotExist) {
		return nil
	}
	if err != nil {
		return err
	}

	var fd fileData
	if err := json.Unmarshal(data, &fd); err != nil {
		return err
	}
	s.notes = fd.Notes
	s.nextID = fd.NextID
	return nil
}

// save writes current state to disk. Caller must hold s.mu.
func (s *Store) save() error {
	fd := fileData{NextID: s.nextID, Notes: s.notes}
	data, err := json.MarshalIndent(fd, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(s.dataFile, data, 0o644)
}

// ── operations (return new slices, never mutate in place) ────────────────────

// List returns all notes (shallow copy).
func (s *Store) List() []Note {
	s.mu.RLock()
	defer s.mu.RUnlock()
	result := make([]Note, len(s.notes))
	copy(result, s.notes)
	return result
}

// Search returns notes whose title, body, or tags contain q (case-insensitive).
func (s *Store) Search(q string) []Note {
	s.mu.RLock()
	defer s.mu.RUnlock()

	q = strings.ToLower(q)
	var result []Note
	for _, n := range s.notes {
		if strings.Contains(strings.ToLower(n.Title), q) ||
			strings.Contains(strings.ToLower(n.Body), q) ||
			containsTag(n.Tags, q) {
			result = append(result, n)
		}
	}
	return result
}

// GetByID returns the note with the given id or ErrNotFound.
func (s *Store) GetByID(id int) (Note, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	for _, n := range s.notes {
		if n.ID == id {
			return n, nil
		}
	}
	return Note{}, ErrNotFound
}

// Create adds a new note and persists. Returns the created note.
func (s *Store) Create(title, body string, tags []string) (Note, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	now := time.Now().UTC().Format(time.RFC3339)
	n := Note{
		ID:        s.nextID,
		Title:     title,
		Body:      body,
		Tags:      normalizeTags(tags),
		CreatedAt: now,
		UpdatedAt: now,
	}
	s.nextID++
	s.notes = append(s.notes, n)
	return n, s.save()
}

// Update replaces title/body/tags for the given id. Returns updated note.
func (s *Store) Update(id int, title, body string, tags []string) (Note, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	idx := -1
	for i, n := range s.notes {
		if n.ID == id {
			idx = i
			break
		}
	}
	if idx < 0 {
		return Note{}, ErrNotFound
	}

	updated := s.notes[idx]
	updated.Title = title
	updated.Body = body
	updated.Tags = normalizeTags(tags)
	updated.UpdatedAt = time.Now().UTC().Format(time.RFC3339)

	// Build new slice without mutating existing entries
	newNotes := make([]Note, len(s.notes))
	copy(newNotes, s.notes)
	newNotes[idx] = updated
	s.notes = newNotes

	return updated, s.save()
}

// Delete removes the note with the given id. Returns ErrNotFound if missing.
func (s *Store) Delete(id int) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	newNotes := make([]Note, 0, len(s.notes))
	found := false
	for _, n := range s.notes {
		if n.ID == id {
			found = true
			continue
		}
		newNotes = append(newNotes, n)
	}
	if !found {
		return ErrNotFound
	}
	s.notes = newNotes
	return s.save()
}

// ── helpers ───────────────────────────────────────────────────────────────────

func normalizeTags(tags []string) []string {
	if tags == nil {
		return []string{}
	}
	seen := make(map[string]struct{}, len(tags))
	result := make([]string, 0, len(tags))
	for _, t := range tags {
		t = strings.ToLower(strings.TrimSpace(t))
		if t == "" {
			continue
		}
		if _, exists := seen[t]; !exists {
			seen[t] = struct{}{}
			result = append(result, t)
		}
	}
	return result
}

func containsTag(tags []string, q string) bool {
	for _, t := range tags {
		if strings.Contains(strings.ToLower(t), q) {
			return true
		}
	}
	return false
}
