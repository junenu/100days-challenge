<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let front = '';
  export let back = '';
  export let submitLabel = '追加';

  const dispatch = createEventDispatcher<{ submit: { front: string; back: string }; cancel: void }>();

  function handleSubmit(e: Event) {
    e.preventDefault();
    const f = front.trim(); const b = back.trim();
    if (!f || !b) return;
    dispatch('submit', { front: f, back: b });
  }
</script>

<form on:submit={handleSubmit} class="form">
  <div class="field">
    <label for="card-front">表面 <span class="required">*</span></label>
    <textarea id="card-front" bind:value={front} placeholder="質問・単語" rows="3" maxlength="400" required></textarea>
  </div>
  <div class="field">
    <label for="card-back">裏面 <span class="required">*</span></label>
    <textarea id="card-back" bind:value={back} placeholder="答え・説明" rows="3" maxlength="400" required></textarea>
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
  textarea {
    padding: .6rem .8rem; border: 1.5px solid var(--border);
    border-radius: 8px; font-size: .95rem; background: var(--bg-card);
    color: var(--text); resize: vertical; font-family: inherit; transition: border-color .2s;
  }
  textarea:focus { outline: none; border-color: var(--accent); }
  .actions { display: flex; justify-content: flex-end; gap: .6rem; margin-top: .5rem; }
  .btn {
    padding: .55rem 1.2rem; border-radius: 8px; border: none;
    font-size: .95rem; font-weight: 600; cursor: pointer; transition: opacity .15s;
  }
  .btn:hover { opacity: .85; }
  .primary { background: var(--accent); color: #fff; }
  .secondary { background: var(--bg-hover); color: var(--text); }
</style>
