
def rank_selectors(element):
    options = []

    if element.get("id"):
        options.append(("id", f'//*[@id="{element["id"]}"]', 1.0))
    
    if element.get("formcontrolname"):
        options.append(("xpath", f'//*[@formcontrolname="{element["formcontrolname"]}"]', 0.95))
    
    if element.get("name"):
        options.append(("name", f'//*[@name="{element["name"]}"]', 0.9))
    
    if element.get("label"):
        options.append(("xpath", f'//label[contains(text(), "{element["label"]}")]/following::input[1]', 0.8))
    
    if "otp-field" in element.get("class", ""):
        options.append(("css", "input.otp-field", 0.98))
    
    if element.get("xpath"):
        options.append(("xpath", element["xpath"], 0.7))

    return sorted(options, key=lambda x: x[2], reverse=True)
