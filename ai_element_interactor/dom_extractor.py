
from selenium.webdriver.remote.webdriver import WebDriver

def extract_all_elements(driver: WebDriver):
    script = """
    function getXPath(element) {
        if (element.id !== '') return '//*[@id="' + element.id + '"]';
        if (element === document.body) return '/html/body';
        let ix = 0;
        const siblings = element.parentNode.childNodes;
        for (let i = 0; i < siblings.length; i++) {
            const sibling = siblings[i];
            if (sibling === element)
                return getXPath(element.parentNode) + '/' + element.tagName + '[' + (ix + 1) + ']';
            if (sibling.nodeType === 1 && sibling.tagName === element.tagName) ix++;
        }
    }

    let elements = [];
    document.querySelectorAll("*").forEach(el => {
        elements.push({
            tag: el.tagName,
            id: el.id,
            name: el.name,
            class: el.className,
            placeholder: el.placeholder || "",
            type: el.type || "",
            text: el.innerText || "",
            aria: el.getAttribute("aria-label") || "",
            xpath: getXPath(el)
        });
    });
    return elements;
    """
    return driver.execute_script(script)
