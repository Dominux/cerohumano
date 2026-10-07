/** @type {import('./$types').PageLoad} */
export function load({ params }) {
  // Captures whatever username string is input after /profile/... in the URL
  return {
    username: params.username,
  }
}
