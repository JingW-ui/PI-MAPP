from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://tjlvnuc7.jsjform.com/f/Thvy0K')
    page.wait_for_load_state('networkidle')

    fields = page.eval_on_selector_all(
        'input[name],select[name],textarea[name]',
        'els => els.map(e=> ({key:e.name, label:e.labels?.[0]?.innerText??"", type:e.type}))'
    )
    print(fields)
    browser.close()