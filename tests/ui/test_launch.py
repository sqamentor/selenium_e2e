def test_launch(browser):
    browser.get("https://bookslot-staging.centerforvein.com/?istestrecord=1")
    assert "Example Domain" in browser.title