function getCookie(cookieKey) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(cookieKey + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(cookieKey.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

export async function postAction(url) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      'X-CSRFToken': getCookie('csrftoken')
    }
  });
  if (!response.ok) return null;
  return await response.json();
}