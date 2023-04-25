"use strict";
function search() {
    const responseElem = document.getElementById("response");
    if (responseElem === null)
        return;
    responseElem.innerHTML = "";
    const regulationElem = document.getElementById("regulation");
    if (regulationElem === null)
        return;
    regulationElem.innerHTML = "";
    const details = document.querySelector("details");
    details.removeAttribute("open");
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
        let i = 0;
        const text = data.response;
        const intervalID = setInterval(() => {
            responseElem.textContent += text.charAt(i);
            i++;
            if (i === text.length)
                clearInterval(intervalID);
            regulationElem.textContent = data.regulation;
        }, 20);
    })
        .catch((error) => console.error(`Error:${error}`));
}
