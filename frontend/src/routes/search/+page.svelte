<!-- src/routes/search/+page.svelte -->
<script>
  import * as Avatar from '#lib/components/ui/avatar'
  import { Input } from '#lib/components/ui/input'
  import { getAbsoluteUrl, getAttachmentUrl } from '#lib/utils.js'
  import { Loader2, Search, ArrowRight } from 'lucide-svelte'

  // Reactive profile stream states
  /** @type {any[]} */
  let users = $state([])
  let searchQuery = $state('')
  let isLoading = $state(true)
  let errorMsg = $state(null)

  // Fetch all profiles from the backend database cluster on mount
  $effect(() => {
    const controller = new AbortController()

    async function fetchAllProfiles() {
      try {
        isLoading = true
        errorMsg = null

        // Request global profiles stream list
        const response = await fetch(getAbsoluteUrl('/api/cerohumanos'), {
          signal: controller.signal,
        })
        if (!response.ok) throw new Error('Failed to load platform directory.')

        users = await response.json()
      } catch (err) {
        if (err.name !== 'AbortError') {
          errorMsg = err.message || 'Failed to sync with api server.'
        }
      } finally {
        isLoading = false
      }
    }

    fetchAllProfiles()
    return () => controller.abort()
  })

  // Client-side computed search filtration filter loop
  let filteredUsers = $derived(
    users.filter((user) => {
      const query = searchQuery.toLowerCase().trim()
      if (!query) return true
      return (
        (user.username || '').toLowerCase().includes(query) ||
        (user.first_name || '').toLowerCase().includes(query) ||
        (user.last_name || '').toLowerCase().includes(query)
      )
    }),
  )
</script>

<div class="h-full w-full bg-white select-none no-scrollbar overflow-y-auto">
  <div class="mx-auto max-w-xl pb-24 pt-4 px-4 text-black">
    <!-- 1. Search Bar Field Dock -->
    <div class="relative mb-6">
      <Search
        class="absolute left-3 top-2.5 h-4 w-4 text-zinc-400 pointer-events-none"
      />
      <Input
        type="text"
        placeholder="Search profiles..."
        bind:value={searchQuery}
        class="pl-10 h-9 bg-zinc-50 border-none text-zinc-900 rounded-lg placeholder:text-zinc-400 focus-visible:ring-1 focus-visible:ring-zinc-200"
      />
    </div>

    <!-- 2. Loading State Element Skeletons -->
    {#if isLoading}
      <div
        class="flex h-[40vh] flex-col items-center justify-center text-zinc-400 gap-2"
      >
        <Loader2 class="h-6 w-6 animate-spin text-zinc-400" />
        <p class="text-xs font-medium tracking-wide">Syncing users list...</p>
      </div>
    {:else if errorMsg}
      <div
        class="rounded-xl border border-red-100 bg-red-50/50 p-4 text-center text-xs text-red-600 font-medium"
      >
        {errorMsg}
      </div>
    {:else if filteredUsers.length === 0}
      <div
        class="text-center py-20 text-xs text-zinc-400 font-medium tracking-wide"
      >
        No matching profiles found.
      </div>
    {:else}
      <!-- 3. Profiles Stream Listing Grid -->
      <div class="space-y-4">
        {#each filteredUsers as user (user.id || user.username)}
          <a
            href="/profile/{user.username}"
            class="flex items-center justify-between p-2 rounded-xl hover:bg-zinc-50 active:scale-[0.99] transition-all duration-150 group"
          >
            <div class="flex items-center gap-4 min-w-0">
              <!-- User Avatar circle -->
              <Avatar.Root class="h-12 w-12 ring-2 ring-zinc-100 shrink-0">
                <Avatar.Image
                  src={getAttachmentUrl(user.profile_picture_id)}
                  alt={user.username}
                  class="object-cover"
                />
                <Avatar.Fallback class="text-sm font-bold bg-zinc-100"
                  >{user.username.slice(0, 2).toUpperCase()}</Avatar.Fallback
                >
              </Avatar.Root>

              <!-- Account Details -->
              <div class="flex flex-col min-w-0">
                <span
                  class="text-sm font-bold text-zinc-900 truncate leading-tight"
                  >{user.username}</span
                >
                <span class="text-xs text-zinc-400 truncate mt-0.5 font-medium">
                  {`${user.first_name} ${user.last_name}` ||
                    'CeroHumano Member'}
                </span>
              </div>
            </div>

            <!-- Action visual indicator icon -->
            <ArrowRight
              class="h-4 w-4 text-zinc-300 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all duration-150"
            />
          </a>
        {/each}
      </div>
    {/if}
  </div>
</div>
