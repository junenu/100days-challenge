// Package handler wires HTTP routes to store operations.
package handler

import (
	"encoding/json"
	"errors"
	"net/http"
	"strconv"
	"strings"

	"notes-api/store"
)

// NewMux returns an http.ServeMux with all routes registered.
func NewMux(s *store.Store) *http.ServeMux {
	mux := http.NewServeMux()

	mux.HandleFunc("/notes", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			handleList(w, r, s)
		case http.MethodPost:
			handleCreate(w, r, s)
		default:
			methodNotAllowed(w)
		}
	})

	mux.HandleFunc("/notes/", func(w http.ResponseWriter, r *http.Request) {
		// /notes/search  →  search endpoint
		if strings.HasSuffix(r.URL.Path, "/search") {
			if r.Method == http.MethodGet {
				handleSearch(w, r, s)
			} else {
				methodNotAllowed(w)
			}
			return
		}

		// /notes/{id}
		id, err := parseID(r.URL.Path, "/notes/")
		if err != nil {
			writeError(w, http.StatusBadRequest, "invalid id")
			return
		}
		switch r.Method {
		case http.MethodGet:
			handleGet(w, r, s, id)
		case http.MethodPut:
			handleUpdate(w, r, s, id)
		case http.MethodDelete:
			handleDelete(w, r, s, id)
		default:
			methodNotAllowed(w)
		}
	})

	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
	})

	return mux
}

// ── request / response types ─────────────────────────────────────────────────

type noteInput struct {
	Title string   `json:"title"`
	Body  string   `json:"body"`
	Tags  []string `json:"tags"`
}

func (n noteInput) validate() string {
	if strings.TrimSpace(n.Title) == "" {
		return "title is required"
	}
	if len(n.Title) > 200 {
		return "title must be 200 characters or fewer"
	}
	return ""
}

// ── handlers ─────────────────────────────────────────────────────────────────

func handleList(w http.ResponseWriter, _ *http.Request, s *store.Store) {
	notes := s.List()
	if notes == nil {
		notes = []store.Note{}
	}
	writeJSON(w, http.StatusOK, map[string]any{"notes": notes, "total": len(notes)})
}

func handleCreate(w http.ResponseWriter, r *http.Request, s *store.Store) {
	var input noteInput
	if err := decodeBody(r, &input); err != nil {
		writeError(w, http.StatusBadRequest, "invalid JSON")
		return
	}
	if msg := input.validate(); msg != "" {
		writeError(w, http.StatusUnprocessableEntity, msg)
		return
	}

	note, err := s.Create(input.Title, input.Body, input.Tags)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to save")
		return
	}
	writeJSON(w, http.StatusCreated, note)
}

func handleGet(w http.ResponseWriter, _ *http.Request, s *store.Store, id int) {
	note, err := s.GetByID(id)
	if errors.Is(err, store.ErrNotFound) {
		writeError(w, http.StatusNotFound, "note not found")
		return
	}
	writeJSON(w, http.StatusOK, note)
}

func handleUpdate(w http.ResponseWriter, r *http.Request, s *store.Store, id int) {
	var input noteInput
	if err := decodeBody(r, &input); err != nil {
		writeError(w, http.StatusBadRequest, "invalid JSON")
		return
	}
	if msg := input.validate(); msg != "" {
		writeError(w, http.StatusUnprocessableEntity, msg)
		return
	}

	note, err := s.Update(id, input.Title, input.Body, input.Tags)
	if errors.Is(err, store.ErrNotFound) {
		writeError(w, http.StatusNotFound, "note not found")
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to save")
		return
	}
	writeJSON(w, http.StatusOK, note)
}

func handleDelete(w http.ResponseWriter, _ *http.Request, s *store.Store, id int) {
	err := s.Delete(id)
	if errors.Is(err, store.ErrNotFound) {
		writeError(w, http.StatusNotFound, "note not found")
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to delete")
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func handleSearch(w http.ResponseWriter, r *http.Request, s *store.Store) {
	q := strings.TrimSpace(r.URL.Query().Get("q"))
	if q == "" {
		writeError(w, http.StatusBadRequest, "q parameter is required")
		return
	}
	notes := s.Search(q)
	if notes == nil {
		notes = []store.Note{}
	}
	writeJSON(w, http.StatusOK, map[string]any{"notes": notes, "total": len(notes), "query": q})
}

// ── helpers ───────────────────────────────────────────────────────────────────

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}

func writeError(w http.ResponseWriter, status int, msg string) {
	writeJSON(w, status, map[string]string{"error": msg})
}

func methodNotAllowed(w http.ResponseWriter) {
	writeError(w, http.StatusMethodNotAllowed, "method not allowed")
}

func decodeBody(r *http.Request, v any) error {
	return json.NewDecoder(r.Body).Decode(v)
}

func parseID(path, prefix string) (int, error) {
	raw := strings.TrimPrefix(path, prefix)
	raw = strings.TrimSuffix(raw, "/")
	return strconv.Atoi(raw)
}
