function getCookie(cookieKey) {            // функция ищет конкретное значение в куках браузера
  let cookieValue = null;                  // создаем переменную для хранения результата, по умолчанию она «пустая»
  if (document.cookie && document.cookie !== "") {    // проверяем: есть ли в браузере вообще какие-либо куки и не пустая ли это строка
    const cookies = document.cookie.split(';');   // куки хранятся в одной длинной строке через точку с запятой. Мы «разрезаем» эту строку в массив отдельных кук
    for (let cookie of cookies) {                 // перебираем каждую куку из полученного массива
      cookie = cookie.trim();                     // удаляем лишние пробелы по краям
      if (cookie.startsWith(cookieKey + "=")) {   // проверяем: начинается ли текущая строка с искомого имени и знака «равно» (например, csrftoken=...)
                                                  // если нашли: вырезаем всё, что идет после знака =, и декодируем спецсимволы в нормальный текст
        cookieValue = decodeURIComponent(cookie.substring(cookieKey.length + 1));
        break;                                     // прерываем цикл, так как нужная кука уже найдена
      }
    }
  }
  return cookieValue;                            // возвращаем найденный токен (или null, если ничего не нашли)
}


export async function getAction(url) {
  const response = await fetch(url);

  if (!response.ok) {
    console.error("Request failed", response.status);
    return null;
  }

  return await response.json();
}


export async function postAction(url, formData = null) {
  const config = {
    method: "POST",
    headers: {
      'X-CSRFToken': getCookie('csrftoken')
    }
  };

  // Добавляем body только если передан formData
  if (formData) {
    config.body = formData;
  }

  const response = await fetch(url, config);

  if (!response.ok) {
    console.error("Request failed", response.status)
    return null;
  }

  return await response.json();
}