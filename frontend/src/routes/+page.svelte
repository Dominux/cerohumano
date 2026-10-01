<script>
  import * as Avatar from '#lib/components/ui/avatar'
  import { Button } from '#lib/components/ui/button'
  import {
    Heart,
    MessageCircle,
    Send,
    Bookmark,
    MoreHorizontal,
  } from 'lucide-svelte'
  import { scale, fade } from 'svelte/transition'

  /**
   * @typedef {Object} Post
   * @property {number} id
   * @property {string} username
   * @property {string} avatarUrl
   * @property {string} location
   * @property {string} imageUrl
   * @property {number} likes
   * @property {boolean} hasLiked
   * @property {boolean} showHeartAnimation
   * @property {string} caption
   * @property {string} timeAgo
   */
  // 1. Create a dynamic reactive state array using Svelte 5 Runes
  /** @type {Post[]} */
  let mockPosts = $state([
    {
      id: 1,
      username: 'svelte_coder',
      avatarUrl: 'https://unsplash.com',
      location: 'San Francisco, CA',
      imageUrl: 'https://unsplash.com',
      likes: 1248,
      hasLiked: false,
      showHeartAnimation: false,
      caption:
        'Building an Instagram clone from scratch using SvelteKit SPA, Tailwind CSS, and shadcn-svelte. The performance on mobile screens is blazing fast! ⚡️📱 #webdev #svelte',
      timeAgo: '2 hours ago',
    },
    {
      id: 2,
      username: 'ui_designer',
      avatarUrl: 'https://unsplash.com',
      location: 'Tokyo, Japan',
      imageUrl: 'https://unsplash.com',
      likes: 932,
      hasLiked: false,
      showHeartAnimation: false,
      caption:
        'Minimalism is not a lack of something. It is simply the perfect amount of something. Love this architectural layout.',
      timeAgo: '5 hours ago',
    },
  ])

  // 2. Track timing logic for mobile double taps
  let lastTap = 0

  /**
   * @param {Post} post
   */
  function handleImageTap(post) {
    const now = Date.now()
    const DOUBLE_TAP_DELAY = 300

    if (now - lastTap < DOUBLE_TAP_DELAY) {
      // Trigger the like action if it hasn't been liked yet
      if (!post.hasLiked) {
        post.likes += 1
        post.hasLiked = true
      }

      // Pop the giant white heart overlay animation framework
      post.showHeartAnimation = true

      setTimeout(() => {
        post.showHeartAnimation = false
      }, 700)
    }
    lastTap = now
  }

  /**
   * @param {Post} post
   */
  function toggleLikeButton(post) {
    if (post.hasLiked) {
      post.likes -= 1
      post.hasLiked = false
    } else {
      post.likes += 1
      post.hasLiked = true
    }
  }
</script>

<div class="mx-auto max-w-md pb-16">
  {#each mockPosts as post (post.id)}
    <article class="mb-2 border-b border-gray-100 bg-white">
      <!-- Post Header Row -->
      <div class="flex items-center justify-between p-3">
        <div class="flex items-center gap-3">
          <Avatar.Root class="h-8 w-8 ring-2 ring-pink-500 ring-offset-2">
            <Avatar.Image
              src={post.avatarUrl}
              alt={post.username}
              class="object-cover"
            />
            <Avatar.Fallback class="bg-zinc-200 text-xs font-semibold">
              {post.username.slice(0, 2).toUpperCase()}
            </Avatar.Fallback>
          </Avatar.Root>
          <div class="flex flex-col">
            <span class="text-xs font-bold leading-none text-zinc-900"
              >{post.username}</span
            >
            {#if post.location}
              <span class="mt-0.5 text-[10px] text-zinc-500 leading-none"
                >{post.location}</span
              >
            {/if}
          </div>
        </div>
        <Button
          variant="ghost"
          size="icon"
          class="h-8 w-8 text-zinc-700 hover:bg-transparent"
        >
          <MoreHorizontal class="h-5 w-5" />
        </Button>
      </div>

      <!-- Post Media Content Area (Handles Double Tap Gestures) -->
      <!-- svelte-ignore a11y_click_events_have_key_events -->
      <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
      <div
        class="relative w-full overflow-hidden bg-zinc-50 aspect-square cursor-pointer select-none"
        onclick={() => handleImageTap(post)}
      >
        <img
          src={post.imageUrl}
          alt="Post content"
          class="h-full w-full object-cover"
          loading="lazy"
        />

        <!-- The Animated Center Pop-up Heart -->
        {#if post.showHeartAnimation}
          <div
            in:scale={{ duration: 250, start: 0.4 }}
            out:fade={{ duration: 200 }}
            class="absolute inset-0 flex items-center justify-center bg-black/10 pointer-events-none"
          >
            <Heart class="h-24 w-24 fill-white stroke-white drop-shadow-lg" />
          </div>
        {/if}
      </div>

      <!-- Interaction Toolbar -->
      <div class="flex items-center justify-between px-3 pt-3">
        <div class="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onclick={() => toggleLikeButton(post)}
            class="h-8 w-8 p-0 hover:bg-transparent active:scale-75 transition-transform duration-150"
          >
            <Heart
              class="h-6 w-6 transition-colors duration-100 {post.hasLiked
                ? 'fill-red-500 stroke-red-500'
                : 'text-zinc-800'}"
            />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            class="h-8 w-8 p-0 text-zinc-800 hover:bg-transparent active:scale-90 transition-transform"
          >
            <MessageCircle class="h-6 w-6" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            class="h-8 w-8 p-0 text-zinc-800 hover:bg-transparent active:scale-90 transition-transform"
          >
            <Send class="h-6 w-6" />
          </Button>
        </div>
        <Button
          variant="ghost"
          size="icon"
          class="h-8 w-8 p-0 text-zinc-800 hover:bg-transparent active:scale-90 transition-transform"
        >
          <Bookmark class="h-6 w-6" />
        </Button>
      </div>

      <!-- Metadata Readout -->
      <div class="px-3 pt-2 pb-4 space-y-1 text-xs">
        <p class="font-bold text-zinc-900">
          {post.likes.toLocaleString()} likes
        </p>
        <p class="text-zinc-800 leading-relaxed">
          <span class="font-bold mr-1.5 text-zinc-900">{post.username}</span>
          {post.caption}
        </p>
        <p
          class="text-[10px] uppercase font-medium tracking-wide text-zinc-400 pt-1"
        >
          {post.timeAgo}
        </p>
      </div>
    </article>
  {/each}
</div>
