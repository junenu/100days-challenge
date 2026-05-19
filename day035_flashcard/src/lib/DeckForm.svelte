<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let name = '';
  export let description = '';
  export let submitLabel = '作成';

  const dispatch = createEventDispatcher<{ submit: { name: string; description: string }; cancel: void }>();

  function handleSubmit(e: Event) {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) return;
    dispatch('submit', { name: trimmed, description: description.trim() });
  }
</script>

<form on:submit={handleSubmit} class="form">
  <div class="field">
    <label for="deck-name">デッキ名 <span class="required">*</span></label>
    <input id="deck-name" bind:value={name} placeholder="例: 英単語 N2" maxlength="60" required />
  </div>
  <div class="field">
    <label for="deck-desc">説明</label>
    <input id="deck-desc" bind:value={description} placeholder="任意" maxlength="120" />
  </div>
  <div class="actions">
    <button type="button" class="btn secondary" on:click={() => dispatch('cancel')}>キャンセル</button>
    <button type="submit" class="btn primary">{submitLabel}</button>
  </div>
</form>

<style>
  .form { display: flex; flex-direction: column; gap: 1rem; }
  .field { display: flex; flex-direction: column; gap: .4rem; }
  label { font-size: .85rem; font-weight: 600; color: var(--text-muted); }
  .required { color: var(--accent); }
  input {
    padding: .6rem .8rem; border: 1.5px solid var(--border);
    border-radius: 8px; font-size: 1rem; background: var(--bg-card);
    color: var(--text); transition: border-color .2s;
  }
  input:focus { outline: none; border-color: var(--accent); }
  .actions { display: flex; justify-content: flex-end; gap: .6rem; margin-top: .5rem; }
  .btn {
    padding: .55rem 1.2rem; border-radius: 8px; border: none;
    font-size: .95rem; font-weight: 600; cursor: pointer; transition: opacity .15s;
  }
  .btn:hover { opacity: .85; }
  .primary { background: var(--accent); color: #fff; }
  .secondary { background: var(--bg-hover); color: var(--text); }
</style>
