from DrissionPage import ChromiumPage, ChromiumOptions
co = ChromiumOptions()
co.set_browser_path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
page = ChromiumPage(co)