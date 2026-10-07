<script>
  import { untrack } from 'svelte'
  import * as Avatar from '#lib/components/ui/avatar'
  import * as Tabs from '#lib/components/ui/tabs'
  import { Separator } from '#lib/components/ui/separator'
  import { Grid, Bookmark, Loader2 } from 'lucide-svelte'
  import { getAttachmentUrl } from '#lib/utils'

  /** @type {{ data: { username: string } }} */
  let { data } = $props()

  // Reactive states for the sequential architecture
  let profileData = $state(null)
  let profilePosts = $state([])

  let isLoadingProfile = $state(true)
  let isLoadingPosts = $state(true)
  let errorMsg = $state(null)

  // Asynchronous sequential waterfall fetching routine
  $effect(() => {
    const controller = new AbortController()

    async function loadProfileDashboardSequential() {
      untrack(async () => {
        try {
          isLoadingProfile = true
          isLoadingPosts = true
          errorMsg = null

          // =========================================================================
          // REQUEST 1: Get User Profile Data by Username
          // =========================================================================
          const infoResponse = await fetch(
            `/api/cerohumanos/by_username/${data.username}`,
            {
              signal: controller.signal,
            },
          )

          if (!infoResponse.ok) throw new Error('Profile info not found.')
          profileData = await infoResponse.json()
          isLoadingProfile = false // Turn off profile loader immediately

          // Verify we got a valid user ID back from the first endpoint
          if (!profileData || !profileData.id) {
            throw new Error(
              'Invalid user profile identifier returned from backend.',
            )
          }

          // =========================================================================
          // REQUEST 2: Get Posts Using the User ID from Request 1
          // =========================================================================
          const postsResponse = await fetch(
            `/api/posts?author_id=${profileData.id}`,
            {
              signal: controller.signal,
            },
          )

          if (postsResponse.ok) {
            profilePosts = await postsResponse.json()
          } else {
            console.error(
              'Failed to fetch profile grid posts array via user ID.',
            )
          }
        } catch (err) {
          if (err.name !== 'AbortError') {
            errorMsg = err.message || 'Failed to sync with network.'
          }
        } finally {
          isLoadingProfile = false
          isLoadingPosts = false
        }
      })
    }

    loadProfileDashboardSequential()
    return () => controller.abort()
  })
</script>

<div
  class="mx-auto max-w-md bg-white pb-24 min-h-screen text-black select-none"
>
  <!-- 1. Profile Info Loading Header Section -->
  {#if isLoadingProfile}
    <div
      class="flex h-[30vh] flex-col items-center justify-center text-zinc-400 gap-2"
    >
      <Loader2 class="h-6 w-6 animate-spin text-zinc-500" />
      <p class="text-xs font-medium tracking-wide">Loading user info...</p>
    </div>
  {:else if errorMsg || !profileData}
    <div
      class="mx-6 my-12 text-center text-xs text-red-600 font-medium p-4 bg-red-50/50 rounded-xl border border-red-100 shadow-none"
    >
      User profile data could not be resolved.
    </div>
  {:else}
    <!-- Header Profile Info Block (Populated via /profile endpoint) -->
    <div class="px-5 pt-6 pb-4">
      <div class="flex items-center justify-between gap-6">
        <!-- Avatar Circle -->
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

        <!-- Stats readouts row -->
        <div class="flex flex-1 justify-around text-center">
          <div class="flex flex-col">
            <span class="text-sm font-bold text-zinc-900"
              >{profilePosts.length ?? 0}</span
            >
            <span class="text-[11px] text-zinc-500 font-medium">posts</span>
          </div>
          <div class="flex flex-col">
            <span class="text-sm font-bold text-zinc-900"
              >{(profileData.followers_count ?? 0).toLocaleString()}</span
            >
            <span class="text-[11px] text-zinc-500 font-medium">followers</span>
          </div>
          <div class="flex flex-col">
            <span class="text-sm font-bold text-zinc-900"
              >{(profileData.following_count ?? 0).toLocaleString()}</span
            >
            <span class="text-[11px] text-zinc-500 font-medium">following</span>
          </div>
        </div>
      </div>

      <!-- User Bio Details -->
      <div class="mt-4 text-xs space-y-0.5">
        <h1 class="font-bold text-zinc-900">
          {profileData.first_name}
          {profileData.last_name}
        </h1>
        <p class="text-zinc-600 leading-relaxed max-w-sm whitespace-pre-wrap">
          {profileData.bio || 'No bio available.'}
        </p>
      </div>
    </div>

    <Separator class="bg-gray-100" />

    <!-- 2. Responsive Instagram Style Image Post Tab-Grid Stream Section -->
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

      <!-- Media Grid Panel (Populated independently via /posts endpoint) -->
      <Tabs.Content value="posts" class="mt-0.5 m-0 p-0 outline-none">
        {#if isLoadingPosts}
          <div class="flex items-center justify-center py-24 text-zinc-400">
            <Loader2 class="h-6 w-6 animate-spin text-zinc-300" />
          </div>
        {:else if !profilePosts || profilePosts.length === 0}
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
                <!-- Render the first attachment thumbnail inside the layout matrix -->
                <img
                  src={getAttachmentUrl(post.attachments[0].id)}
                  alt="Thumbnail"
                  class="h-full w-full object-cover select-none pointer-events-none"
                  loading="lazy"
                />
              </a>
            {/each}
          </div>
        {/if}
      </Tabs.Content>

      <Tabs.Content
        value="saved"
        class="mt-0.5 text-center py-20 text-xs text-zinc-400 font-medium outline-none tracking-wide"
      >
        Private Saved Folders
      </Tabs.Content>
    </Tabs.Root>
  {/if}
</div>
