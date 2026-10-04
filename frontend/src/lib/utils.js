export { cn } from 'cn'

/**
 * Generates an absolute Nginx media URL for a post attachment based on its UUID.
 *
 * @param {string | undefined | null} attachmentId - The UUID string of the attachment record from the backend.
 * @returns {string} The fully formed static HTTP image asset URL string.
 */
export function getAttachmentUrl(attachmentId) {
  if (!attachmentId) {
    // Fallback placeholder image if the attachment ID is missing or broken
    return 'https://unsplash.com'
  }

  const BASE_MEDIA_URL = 'http://localhost:18777/media/images'
  return `${BASE_MEDIA_URL}/${attachmentId}.png`
}
