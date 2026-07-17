const noJSElements = document.querySelectorAll(".no-js");
for (let element of noJSElements) {
    element.classList.remove("no-js");
}

function copyTextToClipboard(text, btnElement) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            showCopiedTooltip(btnElement);
        }).catch(() => {
            fallbackCopyText(text, btnElement);
        });
    } else {
        fallbackCopyText(text, btnElement);
    }
}

function fallbackCopyText(text, btnElement) {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    try {
        document.execCommand("copy");
        showCopiedTooltip(btnElement);
    } catch (err) {
        console.error("Fallback copy failed: ", err);
    }
    document.body.removeChild(textarea);
}

function showCopiedTooltip(btnElement) {
    btnElement.setAttribute("data-copied", "true");
    setTimeout(() => btnElement.removeAttribute("data-copied"), 1500);
}