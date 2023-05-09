const responseElem = document.getElementById("response");
const regulationElem = document.getElementById("regulation");
const details = document.querySelector("details");
const anotherForm = document.getElementById("another-form");

// 関連規約についてさらに質問するフォームを作成
function createAnotherForm() {
  const form = document.createElement("form");
  form.setAttribute("onsubmit", "moreSearch(); return false;");
  form.setAttribute("id", "another-form");
  const input = document.createElement("input");
  input.setAttribute("type", "search");
  input.setAttribute("id", "next-keyword");
  input.setAttribute("placeholder", "詳細についてさらに質問します");
  input.setAttribute("size", "64");
  const submit = document.createElement("input");
  submit.setAttribute("type", "submit");
  submit.setAttribute("id", "next-submit");
  submit.setAttribute("value", "&#xf002;");
  submit.setAttribute("class", "fas");
  form.appendChild(input);
  form.appendChild(submit);
  document.body.appendChild(form);
}

// Reset page
function refresh() {
  regulationElem.innerHTML = "";
  responseElem.innerHTML = "";
  details.removeAttribute("open");
  // anotherForm.innerHTML = "";
}

// バックエンドに規約と回答を問い合わせ
function search() {
  refresh();
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
    .then(createAnotherForm)
    .catch((error) => console.error(`Error:${error}`));
}
