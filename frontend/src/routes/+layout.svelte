<script>
  import './layout.css'
  import { Home, Search, Dices } from 'lucide-svelte'
  import { goto, invalidateAll } from '$app/navigation'
  import { page } from '$app/state'
  import { getAbsoluteUrl } from '#lib/utils.js'

  /** @type {{ children: any }} */
  let { children } = $props()

  const appName = import.meta.env.VITE_APP_NAME || 'CeroHumano'

  /**
   * Handles a smart click routine on the Home logo or menu triggers
   * @param {Event} e
   */
  function handleHomeClick(e) {
    e.preventDefault()

    if (page.url.pathname === '/') {
      const scrollableContainer = document.querySelector('.overflow-y-auto')
      if (scrollableContainer) {
        scrollableContainer.scrollTo({ top: 0, behavior: 'smooth' })
      }
    } else {
      goto('/')
    }
  }

  /**
   * Hits your random endpoint directly on click and forces a clean SvelteKit state refresh
   * @param {Event} e
   */
  async function triggerRandomDiscovery(e) {
    e.preventDefault()

    try {
      // Request a fresh random post object directly from your FastAPI network layer
      const response = await fetch(
        getAbsoluteUrl(`/api/posts/random?t=${Date.now()}`),
      ) // Timestamp breaks browser caching
      if (response.ok) {
        const data = await response.json()
        if (data && data.id) {
          // 1. Force navigation straight to the newly fetched ID path
          await goto(`/posts/${data.id}`)
          // 2. Invalidate all active data loaders to force Svelte to re-fetch the new post parameters instantly
          await invalidateAll()
        }
      }
    } catch (err) {
      console.error('Random navigation pipeline exception:', err)
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
      <a
        href="/search"
        class="p-2 active:scale-90 transition-transform {page.url.pathname ===
        '/search'
          ? 'text-zinc-900'
          : 'text-zinc-400'}"
      >
        <Search
          class="h-6 w-6 {page.url.pathname === '/search'
            ? 'stroke-zinc-900 stroke-[2.5px]'
            : ''}"
        />
      </a>

      <!-- Post Creation Button -->
      <!-- svelte-ignore a11y_invalid_attribute -->
      <a
        href="/posts/random"
        onclick={triggerRandomDiscovery}
        class="p-2 active:scale-90 transition-transform {page.url.pathname.startsWith(
          '/posts/',
        ) && !page.url.pathname.includes('profile')
          ? 'text-zinc-900'
          : 'text-zinc-400'}"
      >
        <Dices
          class="h-6 w-6 {page.url.pathname.startsWith('/posts/') &&
          !page.url.pathname.includes('profile')
            ? 'stroke-zinc-900 stroke-[2.5px]'
            : ''}"
        />
      </a>
    </div>
  </footer>
</div>
