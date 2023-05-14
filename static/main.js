"use strict";
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
    const submit = document.createElement("input");
    submit.setAttribute("type", "submit");
    submit.setAttribute("id", "next-submit");
    submit.setAttribute("value", "&#xf002;");
    submit.setAttribute("class", "fas");
    form.appendChild(input);
    form.appendChild(submit);
    document.body.appendChild(form);
}
function refresh() {
    regulationElem.innerHTML = "";
    responseElem.innerHTML = "";
    details.removeAttribute("open");
    if (anotherForm) {
        anotherForm.innerHTML = "";
    }
}
function search() {
    refresh();
    const keyword = document.getElementById("keyword").value;
    if (keyword === null)
        return;
    fetch(`/ask/${encodeURIComponent(keyword)}`)
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
        const lastContent = data.messages.length - 1;
        const text = data.messages[lastContent].content;
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
