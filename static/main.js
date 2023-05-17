"use strict";
const keywordElem = document.getElementById("keyword");
const queryElem = document.getElementById("query");
const responseElem = document.getElementById("response");
const regulationElem = document.getElementById("regulation");
const details = document.querySelector("details");
const anotherForm = document.getElementById("another-form");
function createAnotherForm() {
    const form = document.createElement("form");
    form.setAttribute("onsubmit", "moreSearch(); return false;");
    form.setAttribute("id", "another-form");
    const input = document.createElement("input");
    input.setAttribute("type", "search");
    input.setAttribute("id", "next-keyword");
    input.setAttribute("placeholder", "詳細についてさらに質問します");
    input.setAttribute("size", "64");
    const icon = document.createElement("i");
    icon.classList.add("fas", "fa-paper-plane");
    const button = document.createElement("button");
    button.appendChild(icon);
    form.appendChild(input);
    form.appendChild(button);
    document.body.appendChild(form);
}
function refreshPage() {
    queryElem.innerHTML = "";
    regulationElem.innerHTML = "";
    responseElem.innerHTML = "";
    details.removeAttribute("open");
    if (anotherForm) {
        anotherForm.innerHTML = "";
    }
}
function search() {
    refreshPage();
    const queryWord = keywordElem.value;
    if (queryWord === null)
        return;
    keywordElem.textContent = "";
    queryElem.textContent = queryWord;
    fetch(`/ask/${encodeURIComponent(queryWord)}`)
        .then((response) => {
        if (response.ok) {
            return response.json();
        }
        else {
            throw new Error(`Net work error ${response.status} ${response.text}`);
        }
    })
        .then((data) => {
        console.debug(data);
        let i = 0;
        const lastIndex = data.messages.length - 1;
        const text = data.messages[lastIndex].content;
        const intervalID = setInterval(() => {
            responseElem.textContent += text.charAt(i);
            i++;
            if (i === text.length)
                clearInterval(intervalID);
            regulationElem.textContent = data.regulation;
        }, 20);
    })
        .then(createAnotherForm)
        .catch((error) => console.error(`Error:${error}`));
}
