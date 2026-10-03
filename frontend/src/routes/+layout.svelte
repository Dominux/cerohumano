<script>
  import './layout.css'
  import { Heart, MessageSquare } from 'lucide-svelte'

  /** @type {{ children: any }} */
  let { children } = $props()
</script>

<!-- Main App Wrapper: Rigid view locked to the dynamic mobile screen height -->
<div
  class="flex h-[100dvh] w-screen flex-col bg-white text-black antialiased overflow-hidden select-none"
>
  <!-- Top Sticky App Header -->
  <header
    class="flex h-12 shrink-0 items-center justify-between border-b border-gray-100 bg-white px-4"
  >
    <!-- styling logo lookalike -->
    <span
      class="font-serif text-2xl font-black italic tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-pink-500 via-red-500 to-yellow-500"
    >
      CeroHumano
    </span>
    <button class="active:scale-90 transition-transform duration-100">
      <Heart class="h-6 w-6 stroke-[2]" />
    </button>
  </header>

  <!-- Scrollable Feed Context Body Layout -->
  <main class="flex-1 overflow-y-auto bg-gray-50/50">
    {@render children()}
  </main>
</div>
