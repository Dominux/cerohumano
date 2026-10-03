<script>
  import * as Avatar from '#lib/components/ui/avatar'
  import { Button } from '#lib/components/ui/button'
  import {
    Heart,
    MessageCircle,
    Send,
    Bookmark,
    MoreHorizontal,
    Loader2,
  } from 'lucide-svelte'

  /**
   * @typedef {Object} Post
   * @property {number} id
   * @property {string} username
   * @property {string} avatarUrl
   * @property {string[]} imageUrls
   * @property {number} activeImageIndex
   * @property {number} likes
   * @property {boolean} hasLiked
   * @property {string} caption
   * @property {string} timeAgo
   */

  // 1. Initialize reactive arrays using Svelte 5 state variables
  /** @type {Post[]} */
  let posts = $state([])
  let isLoading = $state(true)
  /** @type {string | null} */
  let errorMsg = $state(null)

  let lastTap = 0

  // Desktop mouse drag movement configurations
  let isDown = false
  let startX = 0
  let scrollLeft = 0

  // 2. Fetch data from backend on mount using asynchronous effects
  $effect(() => {
    const controller = new AbortController() // Clean cancellation handler

    async function fetchTimeline() {
      try {
        isLoading = true
        // Swap this target placeholder with your actual local or cloud API string
        const response = await fetch('http://localhost:18777/api/posts', {
          signal: controller.signal,
        })

        if (!response.ok) {
          throw new Error(
            `Server returned error status code: ${response.status}`,
          )
        }

        /** @type {any[]} */
        const data = await response.json()

        // Map data ensuring UI engine configurations exist natively
        posts = data.map((post) => ({
          ...post,
          activeImageIndex: post.activeImageIndex ?? 0,
          hasLiked: post.hasLiked ?? false,
        }))
      } catch (err) {
        if (/** @type {Error} */ (err).name !== 'AbortError') {
          errorMsg =
            /** @type {Error} */ (err).message ||
            'Failed to fetch timeline posts data.'
        }
      } finally {
        isLoading = false
      }
    }

    fetchTimeline()

    // Cleanup handler unbinds network requests if user navigates away abruptly
    return () => controller.abort()
  })

  /**
   * Optimistic UI update: communicates interaction state immediately to user
   * @param {Post} post
   */
  async function handleLikeAction(post) {
    if (post.hasLiked) {
      post.likes -= 1
      post.hasLiked = false
    } else {
      post.likes += 1
      post.hasLiked = true
    }

    try {
      // Dispatch state adjustment update upstream back to your DB channel
      await fetch(`http://localhost:3000/api/posts/${post.id}/like`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hasLiked: post.hasLiked }),
      })
    } catch (err) {
      console.error('Backend failed to register user interaction:', err)
      // Optional: Roll back the local UI numbers array state here if database fails explicitly
    }
  }

  /**
   * @param {MouseEvent} e
   * @param {Post} post
   */
  function handleImageClick(e, post) {
    const target = /** @type {HTMLDivElement} */ (e.currentTarget)
    if (target.getAttribute('data-dragged') === 'true') {
      target.removeAttribute('data-dragged')
      return
    }

    const now = Date.now()
    if (now - lastTap < 300) {
      // Double click forces active toggle like
      if (!post.hasLiked) handleLikeAction(post)
    }
    lastTap = now
  }

  /**
   * @param {Event} event
   * @param {Post} post
   */
  function handleCarouselScroll(event, post) {
    const target = /** @type {HTMLDivElement} */ (event.target)
    const index = Math.round(target.scrollLeft / target.clientWidth)
    post.activeImageIndex = index
  }

  /** @param {MouseEvent} e */
  function dragStart(e) {
    const target = /** @type {HTMLDivElement} */ (e.currentTarget)
    isDown = true
    target.classList.remove('scroll-smooth')
    startX = e.pageX - target.offsetLeft
    scrollLeft = target.scrollLeft
  }

  function dragStop() {
    isDown = false
  }

  /** @param {MouseEvent} e */
  function dragMove(e) {
    if (!isDown) return
    e.preventDefault()
    const target = /** @type {HTMLDivElement} */ (e.currentTarget)
    target.setAttribute('data-dragged', 'true')
    const x = e.pageX - target.offsetLeft
    const walk = (x - startX) * 1.5
    target.scrollLeft = scrollLeft - walk
  }
</script>

<div class="mx-auto max-w-md pb-20">
  <!-- 1. Async Loading State Skeleton Spacer -->
  {#if isLoading}
    <div
      class="flex h-[60vh] flex-col items-center justify-center text-zinc-400 gap-2"
    >
      <Loader2 class="h-8 w-8 animate-spin text-zinc-500" />
      <p class="text-sm tracking-wide font-medium">Fetching feed updates...</p>
    </div>

    <!-- 2. Connection Network Errors Indicator Banner -->
  {:else if errorMsg}
    <div
      class="mx-4 my-8 rounded-xl border border-red-100 bg-red-50/50 p-4 text-center text-xs text-red-600"
    >
      <p class="font-bold">Database Sync Warning</p>
      <p class="mt-1 font-medium">{errorMsg}</p>
    </div>

    <!-- 3. Empty Feed State Placeholder -->
  {:else if posts.length === 0}
    <div
      class="flex h-[50vh] flex-col items-center justify-center text-center text-zinc-400 px-6"
    >
      <p class="text-sm font-semibold text-zinc-800">No Posts Available</p>
      <p class="text-xs mt-1 text-zinc-500">
        Your profile network feed is currently waiting for active database
        creation rows.
      </p>
    </div>

    <!-- 4. Active Feed Render Grid Stream -->
  {:else}
    {#each posts as post (post.id)}
      <article class="mb-4 border-b border-gray-100 bg-white">
        <!-- Header Card Details Grid -->
        <div class="flex items-center justify-between p-3">
          <div class="flex items-center gap-3">
            <Avatar.Root class="h-8 w-8 ring-2 ring-pink-500 ring-offset-2">
              <Avatar.Image
                src={post.avatarUrl}
                alt={post.username}
                class="object-cover"
              />
              <Avatar.Fallback
                >{post.username.slice(0, 2).toUpperCase()}</Avatar.Fallback
              >
            </Avatar.Root>
            <span class="text-xs font-bold text-zinc-900">{post.username}</span>
          </div>
          <Button variant="ghost" size="icon" class="h-8 w-8 text-zinc-500"
            ><MoreHorizontal class="h-5 w-5" /></Button
          >
        </div>

        <!-- Media Gallery Core Component Canvas -->
        <div class="relative w-full aspect-[3/4]">
          <div
            class="flex h-full w-full overflow-x-auto snap-x snap-mandatory scroll-smooth no-scrollbar select-none cursor-grab active:cursor-grabbing"
            onscroll={(e) => handleCarouselScroll(e, post)}
            onmousedown={dragStart}
            onmouseleave={dragStop}
            onmouseup={dragStop}
            onmousemove={dragMove}
            onclick={(e) => handleImageClick(e, post)}
          >
            {#each post.imageUrls as imgUrl, index}
              <div
                class="h-full w-full shrink-0 snap-start snap-always relative bg-zinc-50 pointer-events-none"
              >
                <img
                  src={imgUrl}
                  alt="Post content slide"
                  class="h-full w-full object-cover"
                  loading="lazy"
                  draggable="false"
                />
              </div>
            {/each}
          </div>

          {#if post.imageUrls.length > 1}
            <div
              class="absolute top-3 right-3 z-20 rounded-full bg-black/60 px-2 py-1 text-[10px] font-semibold text-white backdrop-blur-sm pointer-events-none tracking-wide"
            >
              {post.activeImageIndex + 1}/{post.imageUrls.length}
            </div>
          {/if}
        </div>

        <!-- Interaction Toolbar Buttons Group Footer -->
        <div class="flex items-center justify-between px-3 pt-3">
          <div class="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onclick={() => handleLikeAction(post)}
              class="h-8 w-8 p-0 hover:bg-transparent active:scale-75 transition-transform"
            >
              <Heart
                class="h-6 w-6 transition-all duration-200 {post.hasLiked
                  ? 'fill-red-500 stroke-red-500 scale-110'
                  : 'text-zinc-800'}"
              />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              class="h-8 w-8 p-0 text-zinc-800 hover:bg-transparent"
              ><MessageCircle class="h-6 w-6" /></Button
            >
            <Button
              variant="ghost"
              size="icon"
              class="h-8 w-8 p-0 text-zinc-800 hover:bg-transparent"
              ><Send class="h-6 w-6" /></Button
            >
          </div>

          {#if post.imageUrls.length > 1}
            <div class="flex items-center gap-1 pointer-events-none">
              {#each post.imageUrls as _, idx}
                <div
                  class="h-1.5 rounded-full transition-all duration-200 {idx ===
                  post.activeImageIndex
                    ? 'w-3 bg-zinc-900'
                    : 'w-1.5 bg-gray-200'}"
                ></div>
              {/each}
            </div>
          {/if}

          <Button
            variant="ghost"
            size="icon"
            class="h-8 w-8 p-0 text-zinc-800 hover:bg-transparent"
            ><Bookmark class="h-6 w-6" /></Button
          >
        </div>

        <!-- Info Text Fields -->
        <div class="px-3 pt-2 pb-4 space-y-1 text-xs">
          <p class="font-bold text-zinc-900">
            {post.likes.toLocaleString()} likes
          </p>
          <p class="text-zinc-800">
            <span class="font-bold mr-1.5">{post.username}</span>{post.caption}
          </p>
          <p
            class="text-[10px] uppercase font-medium tracking-wide text-zinc-400 pt-1"
          >
            {post.timeAgo}
          </p>
        </div>
      </article>
    {/each}
  {/if}
</div>
