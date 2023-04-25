"use strict";
async function print1By1(target, text, intervalTime) {
    let i = 0;
    const intervalID = setInterval(() => {
        target.textContent += text.charAt(i);
        i++;
        if (i === text.length)
            clearInterval(intervalID);
    }, intervalTime);
}
function search() {
    const responseElem = document.getElementById("response");
    if (responseElem === null)
        return;
    responseElem.innerHTML = "";
    const regulationElem = document.getElementById("regulation");
    if (regulationElem === null)
        return;
    regulationElem.innerHTML = "";
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
        .then(async (data) => {
        await print1By1(responseElem, data.response, 20);
        await print1By1(regulationElem, data.regulation, 5);
    })
        .catch((error) => console.error(`Error:${error}`));
}
