<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  export let title = '';
  const dispatch = createEventDispatcher<{ close: void }>();

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Escape') dispatch('close');
  }
</script>

<svelte:window on:keydown={onKey} />

<!-- svelte-ignore a11y_click_events_have_key_events a11y_interactive_supports_focus -->
<div class="overlay" on:click|self={() => dispatch('close')} role="dialog" aria-modal="true" aria-label={title}>
  <div class="modal">
    <div class="modal-header">
      <h2>{title}</h2>
      <button class="close" on:click={() => dispatch('close')} aria-label="閉じる">✕</button>
    </div>
    <div class="modal-body">
      <slot />
    </div>
  </div>
</div>

<style>
  .overlay {
    position: fixed; inset: 0; background: rgba(0,0,0,.45);
    display: flex; align-items: center; justify-content: center;
    z-index: 100; padding: 1rem;
  }
  .modal {
    background: var(--bg-card); border-radius: 14px; width: 100%;
    max-width: 480px; box-shadow: 0 8px 32px rgba(0,0,0,.25);
    overflow: hidden;
  }
  .modal-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 1.25rem; border-bottom: 1px solid var(--border);
  }
  h2 { margin: 0; font-size: 1.1rem; }
  .close {
    background: none; border: none; cursor: pointer; font-size: 1rem;
    color: var(--text-muted); padding: .2rem .4rem; border-radius: 6px;
  }
  .close:hover { background: var(--bg-hover); }
  .modal-body { padding: 1.25rem; }
</style>
