// バックエンドに規約と回答を問い合わせ
function search() {
  // Reset page
  const responseElem = document.getElementById("response");
  if (responseElem === null) return;
  responseElem.innerHTML = "";
  const regulationElem = document.getElementById("regulation");
  if (regulationElem === null) return;
  regulationElem.innerHTML = "";
  const details = document.querySelector("details");
  details.removeAttribute("open");
  // Search keyword
  const keyword = document.getElementById("keyword").value;
  if (keyword === null) return;
  fetch(`/ask/${encodeURIComponent(keyword)}`)
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error(`Net work error ${response.status} ${response.text}`);
      }
    })
    .then((data) => {
      // 20msecごとに一文字ずつtextをresponseElemに表示する
      let i = 0;
      const text = data.response;
      const intervalID = setInterval(() => {
        responseElem.textContent += text.charAt(i);
        i++;
        if (i === text.length) clearInterval(intervalID);
        regulationElem.textContent = data.regulation;
      }, 20);
    })
    .catch((error) => console.error(`Error:${error}`));
}
