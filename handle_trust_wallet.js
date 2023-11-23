// enter mnemonic
const inputWords = document.getElementsByClassName("w-full block flex-1 outline-none bg-transparent title-text font-medium text-left")
for (let i = 0; i < inputWords.length; i++) {
    // create dom
    let newInputWord = document.createElement("input");
    newInputWord.className = "w-full block flex-1 outline-none bg-transparent title-text font-medium text-left";
    newInputWord.type = "text";
    newInputWord.placeholder = "Word #" + (i + 1);
    newInputWord.spellcheck = false;
    newInputWord.defaultValue = "VALUE";

    // assign
    inputWords[i].parentNode.childNodes[0].replaceWith(newInputWord);
}

// click next
document.getElementsByClassName(
    "outline-none bg-primary text-backgroundPrimary hover:bg-primaryHover active:bg-primaryPressed disabled:bg-primaryPressed default-button   w-full"
)[0].click()
