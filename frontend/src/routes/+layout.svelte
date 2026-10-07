<script>
  import './layout.css'
  import { Heart, Home, Search, PlusSquare, User } from 'lucide-svelte'
  import { goto } from '$app/navigation'
  import { page } from '$app/state'

  /** @type {{ children: any }} */
  let { children } = $props()

  const appName = import.meta.env.VITE_APP_NAME || 'CeroHumano'

  /**
   * Handles a smart click routine on the Home logo or menu triggers
   * @param {Event} e
   */
  function handleHomeClick(e) {
    e.preventDefault()

    // --- FIX: Read the pathname directly from the state object (no .subscribe needed!) ---
    if (page.url.pathname === '/') {
      const scrollableContainer = document.querySelector('.overflow-y-auto')
      if (scrollableContainer) {
        scrollableContainer.scrollTo({ top: 0, behavior: 'smooth' })
      }
    } else {
      goto('/')
    }
  }
</script>

<!-- Main App Wrapper: Locked viewport container skeleton context frame -->
<div
  class="flex h-[100dvh] w-screen flex-col bg-zinc-50 text-black antialiased overflow-hidden select-none"
>
  <!--
		===================================================================
		TOP STICKY APP HEADER (Centered Logo Alignment & Feed Width Match)
		===================================================================
	-->
  <header class="w-full shrink-0 border-b border-gray-100 bg-white z-50">
    <div
      class="mx-auto max-w-md h-12 flex items-center justify-center px-4 relative"
    >
      <!-- Dynamic Logo centered perfectly inside the mobile bounding shell -->
      <!-- svelte-ignore a11y_invalid_attribute -->
      <a
        href="/"
        onclick={handleHomeClick}
        class="font-serif text-2xl font-black italic tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-pink-500 via-red-500 to-yellow-500 active:opacity-70 transition-opacity"
      >
        {appName}
      </a>

      <!-- Heart button completely removed from header to align perfectly with request -->
    </div>
  </header>

  <!-- Main Dynamic Feed Content Shell Container Window -->
  <main class="flex-1 overflow-y-auto bg-white">
    {@render children()}
  </main>

  <!--
		===================================================================
		NATIVE MOBILE APPLICATION DOCK APP BAR (Feed Width Match Layout)
		===================================================================
	-->
  <footer class="w-full shrink-0 border-t border-gray-100 bg-white z-40">
    <div
      class="mx-auto max-w-md h-12 pb-safe flex items-center justify-between px-6"
    >
      <!-- Home Tab Icon Link -->
      <!-- svelte-ignore a11y_invalid_attribute -->
      <a
        href="/"
        onclick={handleHomeClick}
        class="p-2 active:scale-90 transition-transform {page.url.pathname ===
        '/'
          ? 'text-zinc-900'
          : 'text-zinc-400'}"
      >
        <Home
          class="h-6 w-6 {page.url.pathname === '/'
            ? 'fill-zinc-900 stroke-zinc-900'
            : ''}"
        />
      </a>

      <!-- Search Button -->
      <button class="p-2 text-zinc-400 active:scale-90 transition-transform">
        <Search class="h-6 w-6" />
      </button>

      <!-- Post Creation Button -->
      <button class="p-2 text-zinc-400 active:scale-90 transition-transform">
        <PlusSquare class="h-6 w-6" />
      </button>
    </div>
  </footer>
</div>
