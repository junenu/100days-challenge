import { writable, derived } from 'svelte/store';
import type { AppState, Card, Deck, StudyRating } from './types';

const STORAGE_KEY = 'flashcard_app_v1';

function generateId(): string {
  return `${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

function loadState(): AppState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return { decks: [], cards: {} };
}

function saveState(state: AppState): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function createStore() {
  const { subscribe, set, update } = writable<AppState>(loadState());

  function persist(state: AppState): AppState {
    saveState(state);
    return state;
  }

  return {
    subscribe,

    addDeck(name: string, description: string): string {
      const id = generateId();
      const deck: Deck = { id, name, description, createdAt: Date.now(), cardIds: [] };
      update(s => persist({ ...s, decks: [...s.decks, deck] }));
      return id;
    },

    updateDeck(id: string, name: string, description: string): void {
      update(s => persist({
        ...s,
        decks: s.decks.map(d => d.id === id ? { ...d, name, description } : d)
      }));
    },

    deleteDeck(id: string): void {
      update(s => {
        const deck = s.decks.find(d => d.id === id);
        const newCards = { ...s.cards };
        if (deck) deck.cardIds.forEach(cid => delete newCards[cid]);
        return persist({ decks: s.decks.filter(d => d.id !== id), cards: newCards });
      });
    },

    addCard(deckId: string, front: string, back: string): string {
      const id = generateId();
      const card: Card = {
        id, front, back,
        createdAt: Date.now(),
        nextReview: Date.now(),
        interval: 1,
        easeFactor: 2.5,
        repetitions: 0,
      };
      update(s => persist({
        cards: { ...s.cards, [id]: card },
        decks: s.decks.map(d => d.id === deckId ? { ...d, cardIds: [...d.cardIds, id] } : d)
      }));
      return id;
    },

    updateCard(id: string, front: string, back: string): void {
      update(s => persist({
        ...s,
        cards: { ...s.cards, [id]: { ...s.cards[id], front, back } }
      }));
    },

    deleteCard(deckId: string, cardId: string): void {
      update(s => {
        const newCards = { ...s.cards };
        delete newCards[cardId];
        return persist({
          cards: newCards,
          decks: s.decks.map(d =>
            d.id === deckId ? { ...d, cardIds: d.cardIds.filter(c => c !== cardId) } : d
          )
        });
      });
    },

    // SM-2 algorithm: update card scheduling based on rating (1=Again, 2=Hard, 3=Good, 4=Easy)
    reviewCard(cardId: string, rating: StudyRating): void {
      update(s => {
        const card = s.cards[cardId];
        if (!card) return s;

        let { interval, easeFactor, repetitions } = card;
        const q = rating - 1; // 0-3 quality for SM-2

        if (q < 2) {
          repetitions = 0;
          interval = 1;
        } else {
          if (repetitions === 0) interval = 1;
          else if (repetitions === 1) interval = 6;
          else interval = Math.round(interval * easeFactor);
          repetitions += 1;
        }

        easeFactor = Math.max(1.3, easeFactor + 0.1 - (3 - q) * (0.08 + (3 - q) * 0.02));

        const nextReview = Date.now() + interval * 24 * 60 * 60 * 1000;
        const updated: Card = { ...card, interval, easeFactor, repetitions, nextReview };
        return persist({ ...s, cards: { ...s.cards, [cardId]: updated } });
      });
    },

    reset(): void {
      localStorage.removeItem(STORAGE_KEY);
      set({ decks: [], cards: {} });
    },

    seed(): void {
      update(s => {
        const deckId = generateId();
        const makeCard = (front: string, back: string): Card => {
          const id = generateId();
          return { id, front, back, createdAt: Date.now(), nextReview: Date.now(), interval: 1, easeFactor: 2.5, repetitions: 0 };
        };
        const cards = [
          makeCard('What is the capital of France?', 'Paris'),
          makeCard('What does HTML stand for?', 'HyperText Markup Language'),
          makeCard('What is 2^10?', '1024'),
          makeCard('Who wrote "The Art of Computer Programming"?', 'Donald Knuth'),
          makeCard('What year was the first iPhone released?', '2007'),
        ];
        const deck: Deck = { id: deckId, name: 'サンプルデッキ', description: 'サンプルカードが含まれています', createdAt: Date.now(), cardIds: cards.map(c => c.id) };
        const newCards = { ...s.cards };
        cards.forEach(c => { newCards[c.id] = c; });
        return persist({ decks: [...s.decks, deck], cards: newCards });
      });
    }
  };
}

export const appStore = createStore();

export const dueCountByDeck = derived(appStore, $s => {
  const now = Date.now();
  const result: Record<string, number> = {};
  for (const deck of $s.decks) {
    result[deck.id] = deck.cardIds.filter(id => ($s.cards[id]?.nextReview ?? 0) <= now).length;
  }
  return result;
});
