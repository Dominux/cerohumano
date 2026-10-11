<script>
  import { untrack } from 'svelte'
  import * as Avatar from '#lib/components/ui/avatar'
  import { Button } from '#lib/components/ui/button'
  import * as Carousel from '#lib/components/ui/carousel'
  import {
    Heart,
    MessageCircle,
    Send,
    Bookmark,
    MoreHorizontal,
    ChevronLeft,
    Loader2,
  } from 'lucide-svelte'
  import { getAttachmentUrl } from '#lib/utils.js'

  /** @type {{ data: { id: string } }} */
  let { data } = $props()

  // Reactive post data states
  let post = $state(null)
  let isLoading = $state(true)
  let errorMsg = $state(null)
  let activeImageIndex = $state(0)
  let lastTap = 0

  $effect(() => {
    const controller = new AbortController()

    async function fetchSinglePost() {
      untrack(async () => {
        try {
          isLoading = true
          errorMsg = null

          // Request detailed parameters for one targeted post ID
          const response = await fetch(`/api/posts/${data.id}`, {
            signal: controller.signal,
          })
          if (!response.ok) throw new Error('This post could not be found.')

          const rawData = await response.json()

          // Format response parameters securely into layout state properties
          post = {
            id: rawData.id,
            username:
              `${rawData.author.first_name} ${rawData.author.last_name}` ||
              'unknown_user',
            avatarUrl: getAttachmentUrl(
              rawData.author.profile_picture_id || '',
            ),
            imageUrls: (rawData.attachments || []).map((att) =>
              getAttachmentUrl(att.id),
            ),
            likes: rawData.likes ?? 0,
            hasLiked: rawData.has_liked || rawData.hasLiked || false,
            caption: rawData.title || '',
            timeAgo: rawData.time_ago || rawData.timeAgo || 'Just now',
          }
        } catch (err) {
          if (err.name !== 'AbortError') {
            errorMsg = err.message || 'Failed to sync with API database.'
          }
        } finally {
          isLoading = false
        }
      })
    }

    fetchSinglePost()
    return () => controller.abort()
  })

  async function handleLikeAction() {
    if (!post) return
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

  function handleDoubleClick() {
    const now = Date.now()
    if (now - lastTap < 300) {
      if (post && !post.hasLiked) handleLikeAction()
    }
    lastTap = now
  }

  function initCarouselApi(api) {
    if (!api) return
    api.on('select', () => {
      activeImageIndex = api.selectedScrollSnap()
    })
  }

  function goBack() {
    window.history.back() // Standard browser navigation back step
  }
</script>

<div
  class="mx-auto max-w-md bg-white min-h-screen text-black select-none pb-12"
>
  <!-- 1. Native Feel Sub-Header Navigation Banner Bar -->
  <header
    class="h-12 border-b border-gray-100 flex items-center px-2 bg-white sticky top-0 z-50"
  >
    <Button
      variant="ghost"
      size="icon"
      onclick={goBack}
      class="h-9 w-9 text-zinc-800"
    >
      <ChevronLeft class="h-6 w-6" />
    </Button>
    <span class="text-sm font-bold text-zinc-900 ml-2">Post</span>
  </header>

  {#if isLoading}
    <div
      class="flex h-[50vh] flex-col items-center justify-center text-zinc-400 gap-2"
    >
      <Loader2 class="h-6 w-6 animate-spin text-zinc-400" />
      <p class="text-xs font-medium">Fetching details...</p>
    </div>
  {:else if errorMsg || !post}
    <div
      class="mx-6 my-12 text-center text-xs text-red-500 font-medium p-4 bg-red-50/50 rounded-xl border border-red-100"
    >
      {errorMsg || 'Post details could not be loaded.'}
    </div>
  {:else}
    <!-- 2. Detailed Single Card View Render -->
    <article class="bg-white">
      <!-- Card Header Layout Info -->
      <div class="flex items-center justify-between p-3">
        <a
          href="/profile/{post.username}"
          class="flex items-center gap-3 hover:opacity-90 transition-opacity"
        >
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
        </a>
        <Button variant="ghost" size="icon" class="h-8 w-8 text-zinc-500"
          ><MoreHorizontal class="h-5 w-5" /></Button
        >
      </div>

      <!-- Embla Drag Carousel Content Shell Container -->
      <!-- svelte-ignore a11y_no_noninteractive_element_interactions, a11y_click_events_have_key_events -->
      <div class="relative w-full aspect-[3/4]" onclick={handleDoubleClick}>
        <Carousel.Root
          setApi={initCarouselApi}
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
            {activeImageIndex + 1}/{post.imageUrls.length}
          </div>
        {/if}
      </div>

      <!-- Actions Toolbar Controls Buttons Footer Row -->
      <div class="flex items-center justify-between px-3 pt-3">
        <div class="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onclick={handleLikeAction}
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
                activeImageIndex
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

      <!-- Text Specifications Block -->
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
  {/if}
</div>
