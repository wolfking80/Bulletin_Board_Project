/**
 * Получение куки по ключу (например, для CSRF-токена Django)
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Универсальный GET запрос
 */
export async function getAction(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error("GET Request failed:", error);
        return null;
    }
}

/**
 * Универсальный POST запрос
 * Поддерживает FormData и обычные объекты (авто-конвертация в JSON)
 */
export async function postAction(url, data = null) {
    const headers = {
        'X-CSRFToken': getCookie('csrftoken'),
    };

    let body = data;

    // Если передали обычный объект (не FormData), превращаем в JSON
    if (data && !(data instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
        body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: headers,
            body: body
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error("POST Request failed:", response.status, errorData);
            return { error: true, status: response.status, data: errorData };
        }

        return await response.json();
    } catch (error) {
        console.error("Network error:", error);
        return { error: true, message: "Network error" };
    }
}
