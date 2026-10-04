<script>
  import * as Avatar from '#lib/components/ui/avatar'
  import { Button } from '#lib/components/ui/button'
  import * as Carousel from '#lib/components/ui/carousel'
  import {
    Heart,
    MessageCircle,
    Send,
    Bookmark,
    MoreHorizontal,
    Loader2,
  } from 'lucide-svelte'
  import { getAttachmentUrl } from '#lib/utils'

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

  let hasMounted = false

  // 1. Reactive stream variables using Svelte 5 Runes
  /** @type {Post[]} */
  let posts = $state([])
  let isLoading = $state(false)
  let errorMsg = $state(null)

  // Pagination Control states
  let offset = $state(0)
  const LIMIT = 5 // Load 5 posts per batch for optimized performance
  let hasMore = $state(true) // Flag to stop fetching if backend is out of items

  let lastTap = 0
  /** @type {HTMLDivElement | null} */
  let scrollContainer = $state(null)

  /**
   * Async fetch loop matching your FastAPI skip/limit architecture
   * @param {boolean} isInitialLoad
   */
  async function fetchTimeline(isInitialLoad = false) {
    if (isLoading || (!hasMore && !isInitialLoad)) return

    try {
      isLoading = true
      if (isInitialLoad) {
        offset = 0
        posts = []
        hasMore = true
      }

      // --- FIX: Lock the current offset target variable and advance it immediately ---
      const currentOffset = offset
      offset += LIMIT

      // Pass limit and offset as parameters to match your router setup
      const response = await fetch(
        `/api/posts?limit=${LIMIT}&offset=${currentOffset}`,
      )
      if (!response.ok)
        throw new Error(`Server connection failed: ${response.status}`)

      const data = await response.json()

      // If backend returns fewer items than requested, we've hit the bottom
      if (!data || data.length < LIMIT) {
        hasMore = false
      }

      // Map and format the incoming Pydantic validation payload records
      /** @type {Post[]} */
      const mappedPosts = (data || []).map((post) => ({
        id: post.id,
        username: post.author.username,
        avatarUrl: getAttachmentUrl(post.author.profile_picture_id),
        // Looks for both backend snake_case or frontend camelCase variants natively
        imageUrls: (post.attachments || []).map((att) =>
          getAttachmentUrl(att.id),
        ),
        activeImageIndex: 0,
        likes: post.likes ?? 0,
        hasLiked: post.has_liked || post.hasLiked || false,
        caption: post.title,
        timeAgo: post.time_ago || 'Just now',
      }))

      // APPEND incoming items instead of overwriting the previous feed
      if (isInitialLoad) {
        posts = mappedPosts
      } else {
        posts = [...posts, ...mappedPosts]
      }
    } catch (err) {
      errorMsg = err.message || 'Failed to pull feed.'
    } finally {
      isLoading = false

      console.log(offset)
    }
  }

  // 2. Trigger initial load on mount automatically
  $effect(() => {
    if (hasMounted) return
    hasMounted = true

    // This forces it to run strictly once on mount, ignoring future reactivity
    fetchTimeline(true)
  })

  /**
   * Detects when the user has scrolled near the bottom of the feed container
   * @param {Event} event
   */
  function handleScrollTrigger(event) {
    if (isLoading || !hasMore) return // --- FIX: Early exit block to stop spamming ---

    const target = /** @type {HTMLDivElement} */ (event.target)
    const threshold = 200
    const isNearBottom =
      target.scrollHeight - target.scrollTop <= target.clientHeight + threshold

    if (isNearBottom) {
      fetchTimeline(false)
    }
  }

  async function handleLikeAction(post) {
    if (post.hasLiked) {
      post.likes -= 1
      post.hasLiked = false
    } else {
      post.likes += 1
      post.hasLiked = true
    }
    try {
      await fetch(`/api/posts/${post.id}/like`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hasLiked: post.hasLiked }),
      })
    } catch (err) {
      console.error('Like error:', err)
    }
  }

  function handleImageDoubleClick(post) {
    const now = Date.now()
    if (now - lastTap < 300) {
      if (!post.hasLiked) handleLikeAction(post)
    }
    lastTap = now
  }

  function initCarouselApi(api, post) {
    if (!api) return
    api.on('select', () => {
      post.activeImageIndex = api.selectedScrollSnap()
    })
  }
</script>

<!--
	CRUCIAL INFINTIE SCROLL FIX:
	Attach the scroll handler to the main scrollable layout container block
-->
<div
  bind:this={scrollContainer}
  onscroll={handleScrollTrigger}
  class="h-full w-full overflow-y-auto px-1 bg-white select-none no-scrollbar"
>
  <div class="mx-auto max-w-md pb-24 pt-2">
    {#if posts.length === 0 && !isLoading && !errorMsg}
      <div
        class="flex h-[50vh] flex-col items-center justify-center text-zinc-400"
      >
        <p class="text-sm font-semibold text-zinc-800">Timeline Empty</p>
      </div>
    {:else}
      {#each posts as post (post.id)}
        <article class="mb-5 border-b border-gray-100 bg-white">
          <!-- Header -->
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
              <span class="text-xs font-bold text-zinc-900"
                >{post.username}</span
              >
            </div>
            <Button variant="ghost" size="icon" class="h-8 w-8 text-zinc-500"
              ><MoreHorizontal class="h-5 w-5" /></Button
            >
          </div>

          <!-- Embla Carousel Media Box -->
          <!-- svelte-ignore a11y_no_noninteractive_element_interactions, a11y_click_events_have_key_events -->
          <div
            class="relative w-full aspect-[3/4]"
            onclick={() => handleImageDoubleClick(post)}
          >
            <Carousel.Root
              setApi={(api) => initCarouselApi(api, post)}
              opts={{ loop: false, watchDrag: true }}
              class="w-full h-full"
            >
              <Carousel.Content class="-ml-0 h-full">
                {#each post.imageUrls as imgUrl, index}
                  <Carousel.Item class="pl-0 h-full w-full basis-full">
                    <div class="h-full w-full relative bg-zinc-50">
                      <img
                        src={imgUrl}
                        alt="Slide {index + 1}"
                        class="h-full w-full object-cover pointer-events-none"
                        loading="lazy"
                      />
                    </div>
                  </Carousel.Item>
                {/each}
              </Carousel.Content>
            </Carousel.Root>

            {#if post.imageUrls && post.imageUrls.length > 1}
              <div
                class="absolute top-3 right-3 z-20 rounded-full bg-black/60 px-2 py-1 text-[10px] font-semibold text-white backdrop-blur-sm tracking-wide"
              >
                {post.activeImageIndex + 1}/{post.imageUrls.length}
              </div>
            {/if}
          </div>

          <!-- Toolbar Buttons -->
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

            {#if post.imageUrls && post.imageUrls.length > 1}
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

          <!-- Post Details -->
          <div class="px-3 pt-2 pb-4 space-y-1 text-xs">
            <p class="font-bold text-zinc-900">
              {post.likes.toLocaleString()} likes
            </p>
            <p class="text-zinc-800">
              <span class="font-bold mr-1.5">{post.username}</span
              >{post.caption}
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

    <!-- 3. Bottom Loading Spinner (Visible while fetching next batch) -->
    {#if isLoading}
      <div
        class="flex w-full items-center justify-center py-4 text-zinc-400 gap-2"
      >
        <Loader2 class="h-5 w-5 animate-spin text-zinc-500" />
        <span class="text-xs font-medium tracking-wide"
          >Loading older posts...</span
        >
      </div>
    {/if}

    <!-- 4. End of Feed Marker -->
    {#if !hasMore && posts.length > 0}
      <div
        class="w-full text-center py-6 text-[11px] font-medium tracking-wide text-zinc-400"
      >
        You've caught up with everyone's posts. ✨
      </div>
    {/if}

    {#if errorMsg}
      <div
        class="mx-4 my-4 rounded-xl border border-red-100 bg-red-50/50 p-3 text-center text-[11px] text-red-600 font-medium"
      >
        {errorMsg}
      </div>
    {/if}
  </div>
</div>
