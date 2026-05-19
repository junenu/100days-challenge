export interface Card {
  id: string;
  front: string;
  back: string;
  createdAt: number;
  nextReview: number;
  interval: number;
  easeFactor: number;
  repetitions: number;
}

export interface Deck {
  id: string;
  name: string;
  description: string;
  createdAt: number;
  cardIds: string[];
}

export type StudyRating = 1 | 2 | 3 | 4;

export interface StudySession {
  deckId: string;
  startedAt: number;
  results: { cardId: string; rating: StudyRating }[];
}

export interface AppState {
  decks: Deck[];
  cards: Record<string, Card>;
}
