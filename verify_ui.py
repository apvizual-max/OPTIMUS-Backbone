import sys
from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Load the local HTML file
        file_path = f"file://{os.path.abspath('90_CONTROL_CENTER/index.html')}"
        page.goto(file_path)

        # Open command palette to render the input
        page.keyboard.press("Control+k")

        # Give it a tiny bit of time to show
        page.wait_for_selector("#palIn", state="visible")

        # Get elements and check their aria-labels
        pal_in_label = page.locator("#palIn").get_attribute("aria-label")
        print(f"Command palette input aria-label: {pal_in_label}")
        if pal_in_label != "Command palette input":
            print("ERROR: Command palette aria-label is incorrect or missing!")
            sys.exit(1)

        # Check AI question box - it's rendered by JS when the tab changes, so let's switch to it
        page.keyboard.press("Escape") # Close palette
        page.click("#btnAsk") # Click Ask button to go to AI tab
        page.wait_for_selector("#aiQ", state="visible")

        ai_q_label = page.locator("#aiQ").get_attribute("aria-label")
        print(f"AI query input aria-label: {ai_q_label}")
        if ai_q_label != "AI query input":
            print("ERROR: AI query aria-label is incorrect or missing!")
            sys.exit(1)

        # The notebook tab is rendered but nbQ only appears if there's nb data, which we don't have mock data for in file://
        # Let's check the HTML string directly for the template file just to be sure we modified it
        with open("MINIMAX OPTIMUS CONTROL CENTER BLUEPRINT/TEMPLATES/index.html", "r") as f:
            content = f.read()
            if 'aria-label="Command palette input"' not in content:
                print("ERROR: Command palette aria-label missing from template!")
                sys.exit(1)
            if 'aria-label="AI query input"' not in content:
                print("ERROR: AI query aria-label missing from template!")
                sys.exit(1)

        print("SUCCESS: All aria-labels are present and correct!")
        browser.close()

if __name__ == "__main__":
    run()
