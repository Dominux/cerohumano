export { cn } from 'cn'

const BASE_URL = 'http://localhost:18777'

/**
 * Generates an absolute Nginx media URL for a post attachment based on its UUID.
 *
 * @param {string} attachmentId - The UUID string of the attachment record from the backend.
 * @returns {string} The fully formed static HTTP image asset URL string.
 */
export function getAttachmentUrl(attachmentId) {
  const BASE_MEDIA_URL = `${BASE_URL}/media/images`
  return `${BASE_MEDIA_URL}/${attachmentId}.png`
}

/**
 * Generates an absolute Nginx API URL
 *
 * @param {string} relativeUri.
 * @returns {string} The fully formed URL string.
 */
export function getAbsoluteUrl(relativeUri) {
  return `${BASE_URL}${relativeUri}`
}

/**
 * Converts an ISO database timestamp into a clean, mobile-optimized "time ago" string.
 * Supports strings like: "Just now", "45m", "3h", "5d", "12w"
 *
 * @param {string | Date | null | undefined} timestamp - The created_at ISO string from the API.
 * @returns {string} Clean, abbreviated human-readable time token string.
 */
export function formatTimeAgo(timestamp) {
  if (!timestamp) return 'Just now'

  const postDate = new Date(timestamp)
  const nowDate = new Date()
  const secondsDiff = Math.floor(
    (nowDate.getTime() - postDate.getTime()) / 1000,
  )

  // Fallback handling if local machine time drifts ahead of the backend database cluster time
  if (secondsDiff < 10) return 'Just now'

  const minutes = Math.floor(secondsDiff / 60)
  if (minutes < 60) return `${minutes}m`

  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h`

  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d`

  const weeks = Math.floor(days / 7)
  return `${weeks}w`
}
