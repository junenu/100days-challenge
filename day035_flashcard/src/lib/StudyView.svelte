<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { get } from 'svelte/store';
  import { appStore } from './store';
  import type { Card, StudyRating } from './types';

  export let deckId: string;
  export let deckName: string;

  const dispatch = createEventDispatcher<{ done: { correct: number; total: number } }>();

  let flipped = false;
  let currentIndex = 0;
  let correct = 0;
  let finished = false;

  function initSession(): Card[] {
    const state = get(appStore);
    const deck = state.decks.find(d => d.id === deckId);
    if (!deck) return [];
    const now = Date.now();
    const due = deck.cardIds
      .map(id => state.cards[id])
      .filter((c): c is Card => !!c && c.nextReview <= now);
    return shuffle([...due]);
  }

  let sessionCards: Card[] = initSession();

  function shuffle<T>(arr: T[]): T[] {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  function flip() {
    flipped = !flipped;
  }

  function rate(rating: StudyRating) {
    const card = sessionCards[currentIndex];
    appStore.reviewCard(card.id, rating);
    if (rating >= 3) correct++;
    currentIndex++;
    flipped = false;
    if (currentIndex >= sessionCards.length) {
      finished = true;
    }
  }

  $: current = sessionCards[currentIndex];
  $: progress = sessionCards.length ? Math.round((currentIndex / sessionCards.length) * 100) : 0;
</script>

<div class="study">
  {#if sessionCards.length === 0}
    <div class="empty-state">
      <div class="icon">🎉</div>
      <p>今日の復習はありません！</p>
      <button class="btn secondary" on:click={() => dispatch('done', { correct: 0, total: 0 })}>戻る</button>
    </div>
  {:else if finished}
    <div class="result">
      <div class="icon">✅</div>
      <h2>セッション完了</h2>
      <p class="score">{correct} / {sessionCards.length} 正解</p>
      <p class="sub">正答率: {Math.round((correct / sessionCards.length) * 100)}%</p>
      <button class="btn primary" on:click={() => dispatch('done', { correct, total: sessionCards.length })}>デッキに戻る</button>
    </div>
  {:else}
    <div class="header">
      <span class="deck-name">{deckName}</span>
      <span class="counter">{currentIndex + 1} / {sessionCards.length}</span>
    </div>
    <div class="progress-bar"><div class="progress-fill" style="width:{progress}%"></div></div>

    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="card-scene" on:click={flip}>
      <div class="card-3d" class:flipped>
        <div class="card-face front">
          <p class="label">表</p>
          <div class="content">{current.front}</div>
          <p class="tap-hint">タップで裏面を見る</p>
        </div>
        <div class="card-face back">
          <p class="label">裏</p>
          <div class="content">{current.back}</div>
        </div>
      </div>
    </div>

    {#if flipped}
      <div class="ratings">
        <p class="rate-label">評価してください</p>
        <div class="rate-buttons">
          <button class="rate again" on:click={() => rate(1)}>
            <span class="rate-key">1</span>
            <span>もう一度</span>
          </button>
          <button class="rate hard" on:click={() => rate(2)}>
            <span class="rate-key">2</span>
            <span>難しい</span>
          </button>
          <button class="rate good" on:click={() => rate(3)}>
            <span class="rate-key">3</span>
            <span>良い</span>
          </button>
          <button class="rate easy" on:click={() => rate(4)}>
            <span class="rate-key">4</span>
            <span>簡単</span>
          </button>
        </div>
      </div>
    {/if}
  {/if}
</div>

<style>
  .study { display: flex; flex-direction: column; align-items: center; gap: 1.2rem; width: 100%; max-width: 560px; margin: 0 auto; }
  .header { width: 100%; display: flex; justify-content: space-between; align-items: center; }
  .deck-name { font-weight: 700; font-size: 1rem; }
  .counter { font-size: .9rem; color: var(--text-muted); }
  .progress-bar { width: 100%; height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; }
  .progress-fill { height: 100%; background: var(--accent); border-radius: 3px; transition: width .3s; }

  .card-scene { width: 100%; height: 240px; perspective: 1000px; cursor: pointer; }
  .card-3d {
    width: 100%; height: 100%; position: relative;
    transform-style: preserve-3d; transition: transform .5s ease;
  }
  .card-3d.flipped { transform: rotateY(180deg); }
  .card-face {
    position: absolute; inset: 0; backface-visibility: hidden;
    background: var(--bg-card); border: 1.5px solid var(--border);
    border-radius: 16px; padding: 1.5rem;
    display: flex; flex-direction: column; justify-content: center; align-items: center;
    box-shadow: 0 4px 16px rgba(0,0,0,.08);
  }
  .card-face.back { transform: rotateY(180deg); background: var(--bg-back); }
  .label { position: absolute; top: 1rem; left: 1.2rem; font-size: .75rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: .05em; }
  .content { font-size: 1.2rem; text-align: center; line-height: 1.6; word-break: break-word; }
  .tap-hint { position: absolute; bottom: 1rem; font-size: .75rem; color: var(--text-muted); }

  .ratings { width: 100%; display: flex; flex-direction: column; align-items: center; gap: .8rem; }
  .rate-label { font-size: .85rem; color: var(--text-muted); margin: 0; }
  .rate-buttons { display: grid; grid-template-columns: repeat(4, 1fr); gap: .6rem; width: 100%; }
  .rate {
    display: flex; flex-direction: column; align-items: center; gap: .2rem;
    padding: .7rem .4rem; border-radius: 10px; border: none; cursor: pointer;
    font-size: .8rem; font-weight: 600; transition: opacity .15s, transform .1s;
  }
  .rate:hover { opacity: .85; transform: translateY(-1px); }
  .rate-key { font-size: 1rem; font-weight: 700; }
  .again { background: #fee2e2; color: #dc2626; }
  .hard { background: #fef3c7; color: #d97706; }
  .good { background: #d1fae5; color: #059669; }
  .easy { background: #dbeafe; color: #2563eb; }

  .empty-state, .result {
    display: flex; flex-direction: column; align-items: center;
    gap: 1rem; padding: 3rem 1rem; text-align: center;
  }
  .icon { font-size: 3rem; }
  .result h2 { margin: 0; }
  .score { font-size: 2rem; font-weight: 700; margin: 0; color: var(--accent); }
  .sub { color: var(--text-muted); margin: 0; }
  .btn {
    padding: .6rem 1.4rem; border-radius: 8px; border: none;
    font-size: .95rem; font-weight: 600; cursor: pointer; transition: opacity .15s;
  }
  .btn:hover { opacity: .85; }
  .primary { background: var(--accent); color: #fff; }
  .secondary { background: var(--bg-hover); color: var(--text); }
</style>
