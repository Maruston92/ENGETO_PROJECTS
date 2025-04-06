import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture()
def browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, slow_mo=1000)
        yield browser
        browser.close()

@pytest.fixture()
def page(browser):
    page = browser.new_page()
    yield page
    page.close()

@pytest.fixture(scope="function")
def close_cookies(page):
    # Otevře stránku a zavře cookies okno
    page.goto("https://engeto.cz/")
    
    # Pokusíme se najít tlačítko pro zavření cookies okna
    cookies_button = page.locator("#cookiescript_reject")
    
    # Počkáme, dokud bude cookies okno viditelné
    try:
        cookies_button.wait_for(state="visible", timeout=10000)  # Časový limit 10 sekund
        cookies_button.click()
        
        # Počkáme, dokud se cookies okno nezmizí
        page.wait_for_selector("#cookiescript_injected", state="detached", timeout=10000)  # Časový limit 10 sekund
    except Exception as e:
        print(f"Cookies okno nešlo zavřít: {e}")
    
    yield page

# Test pro ověření, že stránka se správně načte
def test_page_load(close_cookies):
    page = close_cookies  # Používáme fixture close_cookies
    # Zkontrolujeme, že text v h1 odpovídá očekávanému textu
    page_title = page.inner_text('body > main > div:nth-child(1) > div > div > h1')
    # Nahradíme non-breaking spaces za běžné mezery
    page_title = page_title.replace('\xa0', ' ').strip()
    assert page_title == "Staň se novým IT talentem"

# Test pro ověření přítomnosti konkrétního elementu na stránce
def test_element_present(close_cookies):
    page = close_cookies  # Používáme fixture close_cookies
    # Ověříme, že v navigaci webové stránky je prvek s textem "Kurzy"
    kurzy_element = page.locator('#top-menu > li.area-kurzy.menu-item.menu-item-type-post_type.menu-item-object-page.menu-item-has-children.children-items-type-row > a')
    assert kurzy_element.inner_text() == "Kurzy"

# Test pro ověření přesměrování na jinou stránku
def test_redirect(close_cookies):
    page = close_cookies  # Používáme fixture close_cookies
    # Klikneme na odkaz "Kurzy"
    page.click('text="Kurzy"')
    
    # Počkáme na přesměrování na správnou URL
    page.wait_for_url("https://engeto.cz/prehled-kurzu/")
    
    # Ověříme, že URL je správně přesměrována
    assert page.url == "https://engeto.cz/prehled-kurzu/"
