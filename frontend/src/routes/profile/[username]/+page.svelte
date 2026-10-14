<script>
  import { untrack } from 'svelte'
  import * as Avatar from '#lib/components/ui/avatar'
  import * as Tabs from '#lib/components/ui/tabs'
  import { Separator } from '#lib/components/ui/separator'
  import { Grid, Bookmark, Loader2 } from 'lucide-svelte'
  import { getAbsoluteUrl, getAttachmentUrl } from '#lib/utils.js'

  /** @type {{ data: { username: string } }} */
  let { data } = $props()

  // Reactive states for the sequential architecture
  let profileData = $state(null)
  let profilePosts = $state([])

  let isLoadingProfile = $state(true)
  let isLoadingPosts = $state(true)
  let errorMsg = $state(null)

  // --- FIX: Add Profile Grid Pagination Controllers ---
  let offset = $state(0)
  const LIMIT = 12 // Standard Instagram grid layout batch size (divisible by 3)
  let hasMore = $state(true)
  let fetchLock = false

  /**
   * Sequential fetch routine: Gets user profile metadata first, then kicks off grid posts stream
   */
  $effect(() => {
    const controller = new AbortController()

    async function loadProfileDashboardSequential() {
      untrack(async () => {
        try {
          isLoadingProfile = true
          errorMsg = null

          // 1. Fetch User Profile Info by Username
          const infoResponse = await fetch(
            getAbsoluteUrl(`/api/cerohumanos/by_username/${data.username}`),
            {
              signal: controller.signal,
            },
          )

          if (!infoResponse.ok) throw new Error('Profile info not found.')
          profileData = await infoResponse.json()
          isLoadingProfile = false

          if (!profileData || !profileData.id) {
            throw new Error('Invalid profile identifier.')
          }

          // 2. Kick off the initial batch load of profile grid photos
          await fetchMoreProfilePosts(true, profileData.id, controller.signal)
        } catch (err) {
          if (err.name !== 'AbortError') {
            errorMsg = err.message || 'Failed to sync profile.'
          }
          isLoadingProfile = false
        }
      })
    }

    loadProfileDashboardSequential()
    return () => controller.abort()
  })

  /**
   * --- FIX: Paginated Grid Fetch Engine ---
   * @param {boolean} isInitial
   * @param {string} userId
   * @param {AbortSignal} [signal]
   */
  async function fetchMoreProfilePosts(
    isInitial = false,
    userId = profileData?.id,
    signal = null,
  ) {
    if (fetchLock || (!hasMore && !isInitial) || !userId) return

    fetchLock = true
    isLoadingPosts = true

    try {
      if (isInitial) {
        offset = 0
        profilePosts = []
        hasMore = true
      }

      const currentOffset = offset
      const response = await fetch(
        getAbsoluteUrl(
          `/api/posts?author_id=${userId}&limit=${LIMIT}&offset=${currentOffset}`,
        ),
        { signal },
      )
      if (!response.ok)
        throw new Error('Failed to resolve posts repository stream.')

      const data = await response.json()

      if (!data || data.length < LIMIT) {
        hasMore = false
      }

      if (isInitial) {
        profilePosts = data
      } else {
        profilePosts = [...profilePosts, ...data]
      }

      offset = currentOffset + data.length
    } catch (err) {
      if (err.name !== 'AbortError') console.error(err)
    } finally {
      isLoadingPosts = false
      fetchLock = false
    }
  }

  /**
   * --- FIX: Scroll Intersection Trigger Handler ---
   * @param {Event} event
   */
  function handleProfileScroll(event) {
    if (fetchLock || !hasMore || !profileData?.id) return

    const target = /** @type {HTMLDivElement} */ (event.target)
    const threshold = 150
    const isNearBottom =
      target.scrollHeight - target.scrollTop <= target.clientHeight + threshold

    if (isNearBottom) {
      fetchMoreProfilePosts(false, profileData.id)
    }
  }
</script>

<div
  onscroll={handleProfileScroll}
  class="h-full w-full overflow-y-auto bg-white select-none no-scrollbar"
>
  <div class="mx-auto max-w-md bg-white pb-24 min-h-screen text-black">
    {#if isLoadingProfile}
      <div
        class="flex h-[30vh] flex-col items-center justify-center text-zinc-400 gap-2"
      >
        <Loader2 class="h-6 w-6 animate-spin text-zinc-500" />
        <p class="text-xs font-medium">Loading user info...</p>
      </div>
    {:else if errorMsg || !profileData}
      <div
        class="mx-6 my-12 text-center text-xs text-red-600 font-medium p-4 bg-red-50/50 rounded-xl border border-red-100"
      >
        User profile data could not be resolved.
      </div>
    {:else}
      <!-- Header Profile Info Block (Remains unchanged) -->
      <div class="px-5 pt-6 pb-4">
        <div class="flex items-center justify-between gap-6">
          <Avatar.Root
            class="h-20 w-20 ring-2 ring-zinc-100 ring-offset-2 shrink-0"
          >
            <Avatar.Image
              src={getAttachmentUrl(profileData.profile_picture_id)}
              alt={data.username}
              class="object-cover"
            />
            <Avatar.Fallback class="text-xl font-bold"
              >{data.username.slice(0, 2).toUpperCase()}</Avatar.Fallback
            >
          </Avatar.Root>

          <div class="flex flex-1 justify-around text-center">
            <div class="flex flex-col">
              <span class="text-sm font-bold text-zinc-900"
                >{profileData.posts_count ?? 0}</span
              >
              <span class="text-[11px] text-zinc-500 font-medium">posts</span>
            </div>
            <div class="flex flex-col">
              <span class="text-sm font-bold text-zinc-900"
                >{(profileData.followers_count ?? 0).toLocaleString()}</span
              >
              <span class="text-[11px] text-zinc-500 font-medium"
                >followers</span
              >
            </div>
            <div class="flex flex-col">
              <span class="text-sm font-bold text-zinc-900"
                >{(profileData.following_count ?? 0).toLocaleString()}</span
              >
              <span class="text-[11px] text-zinc-500 font-medium"
                >following</span
              >
            </div>
          </div>
        </div>

        <div class="mt-4 text-xs space-y-0.5">
          <h1 class="font-bold text-zinc-900">
            {data.username}
          </h1>
          <p class="text-zinc-600 leading-relaxed max-w-sm whitespace-pre-wrap">
            {profileData.first_name + ' ' + profileData.last_name}
          </p>
        </div>
      </div>

      <Separator class="bg-gray-100" />

      <!-- Responsive Post Tab-Grid Stream Section -->
      <Tabs.Root value="posts" class="w-full">
        <Tabs.List
          class="w-full h-10 bg-transparent rounded-none p-0 flex border-b border-gray-100"
        >
          <Tabs.Trigger
            value="posts"
            class="flex-1 h-full bg-transparent rounded-none border-b-2 border-transparent data-[state=active]:border-zinc-900 data-[state=active]:bg-transparent data-[state=active]:shadow-none text-zinc-400 data-[state=active]:text-zinc-900 p-0"
          >
            <Grid class="h-5 w-5" />
          </Tabs.Trigger>
          <Tabs.Trigger
            value="saved"
            class="flex-1 h-full bg-transparent rounded-none border-b-2 border-transparent data-[state=active]:border-zinc-900 data-[state=active]:bg-transparent data-[state=active]:shadow-none text-zinc-400 data-[state=active]:text-zinc-900 p-0"
          >
            <Bookmark class="h-5 w-5" />
          </Tabs.Trigger>
        </Tabs.List>

        <!-- Media Grid Panel -->
        <Tabs.Content value="posts" class="mt-0.5 m-0 p-0 outline-none">
          {#if profilePosts.length === 0 && !isLoadingPosts}
            <div
              class="text-center py-20 text-xs text-zinc-400 font-medium tracking-wide"
            >
              No Posts Yet
            </div>
          {:else}
            <div class="grid grid-cols-3 gap-0.5">
              {#each profilePosts as post (post.id)}
                <a
                  href="/posts/{post.id}"
                  class="aspect-square bg-zinc-50 relative group overflow-hidden active:opacity-80 transition-opacity"
                >
                  <img
                    src={getAttachmentUrl(post.attachments[0]?.id)}
                    alt="Thumbnail"
                    class="h-full w-full object-cover select-none pointer-events-none"
                    loading="lazy"
                  />
                </a>
              {/each}
            </div>
          {/if}

          <!-- --- CHANGE: Add dynamic micro-loader for older grid page batches --- -->
          {#if isLoadingPosts}
            <div
              class="flex w-full items-center justify-center py-6 text-zinc-400"
            >
              <Loader2 class="h-5 w-5 animate-spin text-zinc-300" />
            </div>
          {/if}
        </Tabs.Content>

        <Tabs.Content
          value="saved"
          class="mt-0.5 text-center py-20 text-xs text-zinc-400 font-medium outline-none"
        >
          Private Saved Folders
        </Tabs.Content>
      </Tabs.Root>
    {/if}
  </div>
</div>
