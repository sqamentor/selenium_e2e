def rank_selectors(element):
    options = []

    if element.get("id"):
        options.append(("id", f'//*[@id="{element["id"]}"]', 1.0))
    if element.get("name"):
        options.append(("name", f'//*[@name="{element["name"]}"]', 0.9))
    if element.get("xpath"):
        options.append(("xpath", element["xpath"], 0.8))

    return sorted(options, key=lambda x: x[2], reverse=True)
