<script>
  import * as Avatar from '#lib/components/ui/avatar'
  import { Button } from '#lib/components/ui/button'
  import * as Carousel from '#lib/components/ui/carousel'
  import { getAttachmentUrl } from '#lib/utils.js'
  import {
    Heart,
    MessageCircle,
    Send,
    Bookmark,
    MoreHorizontal,
    Loader2,
  } from 'lucide-svelte'

  // 1. Properly initialized reactive states
  /** @type {any[]} */
  let posts = $state([])
  let isLoading = $state(true)
  /** @type {string | null} */
  let errorMsg = $state(null)

  let lastTap = 0
  let isDown = false
  let startX = 0
  let scrollLeft = 0

  $effect(() => {
    const controller = new AbortController()

    async function fetchTimeline() {
      try {
        isLoading = true
        // Hitting the local Nginx proxy endpoint directly
        const response = await fetch('http://localhost:18777/api/posts', {
          signal: controller.signal,
        })

        if (!response.ok) {
          throw new Error(
            `Server returned error status code: ${response.status}`,
          )
        }

        const data = await response.json()

        // 2. Safe mapping array with explicit fallbacks for snake_case/camelCase variants
        posts = (data || []).map((post) => ({
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
          timeAgo: post.time_ago || post.timeAgo || 'Just now',
        }))
      } catch (err) {
        if (err.name !== 'AbortError') {
          errorMsg = err.message || 'Failed to parse layout.'
        }
      } finally {
        isLoading = false
      }
    }

    fetchTimeline()
    return () => controller.abort()
  })

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
      console.error('Like tracking failed:', err)
    }
  }

  /** @param {Post} post */
  function handleImageDoubleClick(post) {
    const now = Date.now()
    if (now - lastTap < 300) {
      if (!post.hasLiked) handleLikeAction(post)
    }
    lastTap = now
  }

  /**
   * Capture active indexing snapshots directly out of Embla's API engine hooks
   * @param {any} api - The Embla API instance object reference
   * @param {Post} post
   */
  function initCarouselApi(api, post) {
    if (!api) return
    api.on('select', () => {
      post.activeImageIndex = api.selectedScrollSnap()
    })
  }
</script>

<div class="mx-auto max-w-md pb-20">
  {#if isLoading}
    <div
      class="flex h-[60vh] flex-col items-center justify-center text-zinc-400 gap-2"
    >
      <Loader2 class="h-8 w-8 animate-spin text-zinc-500" />
      <p class="text-sm font-medium">Loading CeroHumano...</p>
    </div>
  {:else if errorMsg}
    <div
      class="mx-4 my-8 rounded-xl border border-red-100 bg-red-50/50 p-4 text-center text-xs text-red-600"
    >
      <p class="font-bold">App Error</p>
      <p class="mt-1 font-medium">{errorMsg}</p>
    </div>
  {:else}
    {#each posts as post (post.id)}
      <article class="mb-4 border-b border-gray-100 bg-white">
        <!-- Post Header -->
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

        <!--
					Embla Powered Media Slider Box:
					- Handles multi-device drag inertia natively
					- setApi hooks into index adjustments automatically
				-->
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
                  <div class="h-full w-full relative bg-zinc-50 select-none">
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

          <!-- Absolute Position Counter Overlay -->
          {#if post.imageUrls && post.imageUrls.length > 1}
            <div
              class="absolute top-3 right-3 z-20 rounded-full bg-black/60 px-2 py-1 text-[10px] font-semibold text-white backdrop-blur-sm pointer-events-none tracking-wide"
            >
              {post.activeImageIndex + 1}/{post.imageUrls.length}
            </div>
          {/if}
        </div>

        <!-- Actions Footer Buttons Toolbar -->
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

          <!-- Carousel Pagination Indicator Dots -->
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

        <!-- Information Captions -->
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
