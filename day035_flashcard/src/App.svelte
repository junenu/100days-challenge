<script lang="ts">
  import { appStore, dueCountByDeck } from './lib/store';
  import Modal from './lib/Modal.svelte';
  import DeckForm from './lib/DeckForm.svelte';
  import CardForm from './lib/CardForm.svelte';
  import StudyView from './lib/StudyView.svelte';

  type View = 'home' | 'deck' | 'study';
  let view: View = 'home';
  let selectedDeckId = '';

  let showNewDeck = false;
  let showEditDeck = false;
  let showNewCard = false;
  let editCardId = '';
  let showDeleteDeck = false;
  let deleteCardId = '';

  $: state = $appStore;
  $: dueCounts = $dueCountByDeck;
  $: selectedDeck = state.decks.find(d => d.id === selectedDeckId);
  $: selectedCards = selectedDeck ? selectedDeck.cardIds.map(id => state.cards[id]).filter(Boolean) : [];

  function openDeck(id: string) {
    selectedDeckId = id;
    view = 'deck';
  }

  function startStudy() {
    view = 'study';
  }

  function onStudyDone(_e: CustomEvent<{ correct: number; total: number }>) {
    view = 'deck';
  }

  function createDeck(e: CustomEvent<{ name: string; description: string }>) {
    appStore.addDeck(e.detail.name, e.detail.description);
    showNewDeck = false;
  }

  function editDeck(e: CustomEvent<{ name: string; description: string }>) {
    appStore.updateDeck(selectedDeckId, e.detail.name, e.detail.description);
    showEditDeck = false;
  }

  function confirmDeleteDeck() {
    appStore.deleteDeck(selectedDeckId);
    showDeleteDeck = false;
    view = 'home';
  }

  function createCard(e: CustomEvent<{ front: string; back: string }>) {
    appStore.addCard(selectedDeckId, e.detail.front, e.detail.back);
    showNewCard = false;
  }

  function openEditCard(cardId: string) {
    editCardId = cardId;
  }

  function saveCard(e: CustomEvent<{ front: string; back: string }>) {
    appStore.updateCard(editCardId, e.detail.front, e.detail.back);
    editCardId = '';
  }

  function confirmDeleteCard() {
    appStore.deleteCard(selectedDeckId, deleteCardId);
    deleteCardId = '';
  }

  $: editCard = editCardId ? state.cards[editCardId] : null;

  function formatDate(ts: number) {
    return new Date(ts).toLocaleDateString('ja-JP');
  }

  function isDue(ts: number) {
    return ts <= Date.now();
  }
</script>

<div class="app">
  <header>
    <div class="header-inner">
      <button class="logo" on:click={() => { view = 'home'; selectedDeckId = ''; }}>
        🃏 FlashCard
      </button>
      {#if view === 'deck' && selectedDeck}
        <span class="breadcrumb">/ {selectedDeck.name}</span>
      {/if}
      {#if view === 'study' && selectedDeck}
        <span class="breadcrumb">/ {selectedDeck.name} / 学習中</span>
      {/if}
    </div>
  </header>

  <main>
    {#if view === 'home'}
      <div class="page">
        <div class="page-header">
          <h1>デッキ一覧</h1>
          <div class="page-actions">
            {#if state.decks.length === 0}
              <button class="btn secondary" on:click={() => appStore.seed()}>サンプルを追加</button>
            {/if}
            <button class="btn primary" on:click={() => showNewDeck = true}>+ 新しいデッキ</button>
          </div>
        </div>

        {#if state.decks.length === 0}
          <div class="empty">
            <p>デッキがありません。</p>
            <p class="sub">「+ 新しいデッキ」または「サンプルを追加」で始めましょう。</p>
          </div>
        {:else}
          <div class="deck-grid">
            {#each state.decks as deck}
              {@const due = dueCounts[deck.id] ?? 0}
              <button class="deck-card" on:click={() => openDeck(deck.id)}>
                <div class="deck-top">
                  <span class="deck-name">{deck.name}</span>
                  {#if due > 0}
                    <span class="badge due">{due}</span>
                  {/if}
                </div>
                {#if deck.description}
                  <p class="deck-desc">{deck.description}</p>
                {/if}
                <div class="deck-meta">
                  <span>{deck.cardIds.length} 枚</span>
                  <span>{formatDate(deck.createdAt)}</span>
                </div>
              </button>
            {/each}
          </div>
        {/if}
      </div>

    {:else if view === 'deck' && selectedDeck}
      <div class="page">
        <div class="page-header">
          <div class="back-row">
            <button class="back" on:click={() => { view = 'home'; selectedDeckId = ''; }}>← 戻る</button>
            <h1>{selectedDeck.name}</h1>
          </div>
          <div class="page-actions">
            <button class="btn ghost" on:click={() => showEditDeck = true}>編集</button>
            <button class="btn ghost danger-ghost" on:click={() => showDeleteDeck = true}>削除</button>
            <button class="btn secondary" on:click={() => showNewCard = true}>+ カード追加</button>
            {#if (dueCounts[selectedDeckId] ?? 0) > 0}
              <button class="btn primary" on:click={startStudy}>
                学習開始 ({dueCounts[selectedDeckId]})
              </button>
            {:else}
              <button class="btn primary" on:click={startStudy}>学習する</button>
            {/if}
          </div>
        </div>

        {#if selectedDeck.description}
          <p class="deck-description">{selectedDeck.description}</p>
        {/if}

        {#if selectedCards.length === 0}
          <div class="empty">
            <p>カードがありません。</p>
            <p class="sub">「+ カード追加」でカードを作成してください。</p>
          </div>
        {:else}
          <div class="card-list">
            {#each selectedCards as card}
              <div class="card-item" class:due={isDue(card.nextReview)}>
                <div class="card-content">
                  <div class="card-front">{card.front}</div>
                  <div class="card-back">{card.back}</div>
                </div>
                <div class="card-actions">
                  <span class="card-meta">次回: {isDue(card.nextReview) ? '今日' : formatDate(card.nextReview)}</span>
                  <button class="icon-btn" on:click={() => openEditCard(card.id)} title="編集">✏️</button>
                  <button class="icon-btn" on:click={() => (deleteCardId = card.id)} title="削除">🗑️</button>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

    {:else if view === 'study' && selectedDeck}
      <div class="page study-page">
        <button class="back" on:click={() => { view = 'deck'; }}>← 中断して戻る</button>
        <StudyView deckId={selectedDeckId} deckName={selectedDeck.name} on:done={onStudyDone} />
      </div>
    {/if}
  </main>
</div>

<!-- Modals -->
{#if showNewDeck}
  <Modal title="新しいデッキ" on:close={() => (showNewDeck = false)}>
    <DeckForm on:submit={createDeck} on:cancel={() => (showNewDeck = false)} />
  </Modal>
{/if}

{#if showEditDeck && selectedDeck}
  <Modal title="デッキを編集" on:close={() => (showEditDeck = false)}>
    <DeckForm name={selectedDeck.name} description={selectedDeck.description} submitLabel="保存"
      on:submit={editDeck} on:cancel={() => (showEditDeck = false)} />
  </Modal>
{/if}

{#if showDeleteDeck}
  <Modal title="デッキを削除" on:close={() => (showDeleteDeck = false)}>
    <p>「{selectedDeck?.name}」とすべてのカードを削除しますか？</p>
    <div style="display:flex;justify-content:flex-end;gap:.6rem;margin-top:1rem">
      <button class="btn secondary" on:click={() => (showDeleteDeck = false)}>キャンセル</button>
      <button class="btn danger" on:click={confirmDeleteDeck}>削除する</button>
    </div>
  </Modal>
{/if}

{#if showNewCard}
  <Modal title="カードを追加" on:close={() => (showNewCard = false)}>
    <CardForm on:submit={createCard} on:cancel={() => (showNewCard = false)} />
  </Modal>
{/if}

{#if editCard}
  <Modal title="カードを編集" on:close={() => (editCardId = '')}>
    <CardForm front={editCard.front} back={editCard.back} submitLabel="保存"
      on:submit={saveCard} on:cancel={() => (editCardId = '')} />
  </Modal>
{/if}

{#if deleteCardId}
  <Modal title="カードを削除" on:close={() => (deleteCardId = '')}>
    <p>このカードを削除しますか？</p>
    <div style="display:flex;justify-content:flex-end;gap:.6rem;margin-top:1rem">
      <button class="btn secondary" on:click={() => (deleteCardId = '')}>キャンセル</button>
      <button class="btn danger" on:click={confirmDeleteCard}>削除する</button>
    </div>
  </Modal>
{/if}

<style>
  :global(*) { box-sizing: border-box; }
  :global(:root) {
    --accent: #6366f1;
    --bg: #f8f9fb;
    --bg-card: #ffffff;
    --bg-back: #f0f4ff;
    --bg-hover: #f1f2f6;
    --text: #1a1b2e;
    --text-muted: #6b7280;
    --border: #e5e7eb;
  }
  :global(body) {
    margin: 0; font-family: 'Segoe UI', system-ui, sans-serif;
    background: var(--bg); color: var(--text);
  }
  .app { min-height: 100vh; display: flex; flex-direction: column; }

  header {
    background: var(--bg-card); border-bottom: 1px solid var(--border);
    position: sticky; top: 0; z-index: 10;
  }
  .header-inner { max-width: 860px; margin: 0 auto; padding: .8rem 1.2rem; display: flex; align-items: center; gap: .5rem; }
  .logo { background: none; border: none; font-size: 1.2rem; font-weight: 800; cursor: pointer; color: var(--accent); padding: 0; }
  .breadcrumb { color: var(--text-muted); font-size: .95rem; }

  main { flex: 1; }
  .page { max-width: 860px; margin: 0 auto; padding: 1.5rem 1.2rem; }
  .study-page { padding-top: 1rem; }

  .page-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
  h1 { margin: 0; font-size: 1.6rem; }
  .page-actions { display: flex; gap: .5rem; flex-wrap: wrap; align-items: center; }

  .back-row { display: flex; align-items: center; gap: .8rem; }
  .back { background: none; border: none; cursor: pointer; color: var(--accent); font-size: .95rem; font-weight: 600; padding: 0; }
  .back:hover { text-decoration: underline; }

  .deck-description { color: var(--text-muted); margin: 0 0 1.2rem; }

  .deck-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; }
  .deck-card {
    background: var(--bg-card); border: 1.5px solid var(--border); border-radius: 14px;
    padding: 1.1rem; text-align: left; cursor: pointer; transition: box-shadow .2s, border-color .2s;
    display: flex; flex-direction: column; gap: .5rem;
  }
  .deck-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.08); border-color: var(--accent); }
  .deck-top { display: flex; align-items: center; justify-content: space-between; }
  .deck-name { font-weight: 700; font-size: 1rem; }
  .badge { padding: .15rem .5rem; border-radius: 20px; font-size: .75rem; font-weight: 700; }
  .badge.due { background: var(--accent); color: #fff; }
  .deck-desc { margin: 0; font-size: .85rem; color: var(--text-muted); }
  .deck-meta { display: flex; justify-content: space-between; font-size: .8rem; color: var(--text-muted); margin-top: auto; }

  .card-list { display: flex; flex-direction: column; gap: .6rem; }
  .card-item {
    background: var(--bg-card); border: 1.5px solid var(--border); border-radius: 12px;
    padding: .9rem 1rem; display: flex; justify-content: space-between; align-items: center; gap: 1rem;
  }
  .card-item.due { border-left: 4px solid var(--accent); }
  .card-content { flex: 1; min-width: 0; }
  .card-front { font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .card-back { font-size: .85rem; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .card-actions { display: flex; align-items: center; gap: .5rem; flex-shrink: 0; }
  .card-meta { font-size: .75rem; color: var(--text-muted); white-space: nowrap; }
  .icon-btn { background: none; border: none; cursor: pointer; font-size: 1rem; padding: .2rem .3rem; border-radius: 6px; }
  .icon-btn:hover { background: var(--bg-hover); }

  .empty { text-align: center; padding: 3rem 1rem; color: var(--text-muted); }
  .empty p { margin: .3rem 0; }
  .empty .sub { font-size: .9rem; }

  .btn {
    padding: .5rem 1rem; border-radius: 8px; border: none;
    font-size: .9rem; font-weight: 600; cursor: pointer; transition: opacity .15s;
    white-space: nowrap;
  }
  .btn:hover { opacity: .85; }
  .primary { background: var(--accent); color: #fff; }
  .secondary { background: var(--bg-hover); color: var(--text); }
  .ghost { background: none; color: var(--text-muted); border: 1px solid var(--border); }
  .danger-ghost { color: #ef4444; border-color: #ef4444; }
  .danger { background: #ef4444; color: #fff; }
</style>
