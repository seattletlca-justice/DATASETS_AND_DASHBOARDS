"""
STLCA Portal DOM Probe
Loads one record's Status tab and Related Records tab and dumps:
  1. The onclick ancestor chain for "Complaint Intake"
  2. The first 5000 chars of HTML from the status section
  3. The View Details link details
  4. What changes in visible text AFTER clicking View Details (delta approach)

Run from stlca_web root:
  python SCRIPTS/portal_dom_probe.py
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ── Use the Lowell NOV — it has inspections AND related records ──────────────
TEST_RECORD = '1055976-VI'
TEST_URL    = f'https://services.seattle.gov/portal/customize/LinkToRecord.aspx?altId={TEST_RECORD}&RecordGroup=1'
OUT_FILE    = 'SCRIPTS/dom_probe_output.txt'
# ─────────────────────────────────────────────────────────────────────────────

def make_driver():
    opts = Options()
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_experimental_option('excludeSwitches', ['enable-automation'])
    opts.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )
    driver.set_window_size(1400, 900)
    return driver


def click_tab(driver, label):
    els = driver.find_elements(By.TAG_NAME, 'a')
    for el in els:
        if label.lower() in el.text.strip().lower() and el.is_displayed():
            driver.execute_script("arguments[0].scrollIntoView(true);", el)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", el)
            return True
    return False


lines = []

def log(msg=''):
    print(msg)
    lines.append(str(msg))


driver = make_driver()

try:
    # ── 1. Load page ──────────────────────────────────────────────────────────
    log('=' * 70)
    log(f'Loading: {TEST_URL}')
    driver.get(TEST_URL)
    time.sleep(8)
    log(f'Title: {driver.title}')

    # ── 2. Click Status tab ───────────────────────────────────────────────────
    log()
    log('=' * 70)
    log('Clicking Status tab...')
    click_tab(driver, 'Status')
    time.sleep(5)

    # ── 3. Find the onclick ancestor for step names ───────────────────────────
    log()
    log('=' * 70)
    log('STEP NAME ONCLICK PROBE:')

    STEP_KEYWORDS = [
        'Complaint Intake', 'Pre-NOV Actions', 'Issue NOV', 'Follow-up Investigation',
        'Prep to Close', 'Closed',
    ]

    for kw in STEP_KEYWORDS:
        result = driver.execute_script(f"""
            var kw = arguments[0];
            // Find leaf text node containing this keyword
            var walker = document.createTreeWalker(
                document.body, NodeFilter.SHOW_TEXT, null, false
            );
            var node;
            while (node = walker.nextNode()) {{
                if (node.textContent.trim().indexOf(kw) >= 0 &&
                    node.textContent.trim().length < 80) {{
                    // Walk up to find first clickable ancestor
                    var el = node.parentElement;
                    var chain = [];
                    for (var i = 0; i < 12; i++) {{
                        if (!el) break;
                        var info = {{
                            tag: el.tagName,
                            id: el.id,
                            cls: el.className.toString().substring(0, 80),
                            onclick: (el.getAttribute('onclick') || '').substring(0, 100),
                            href: el.getAttribute('href') || '',
                            role: el.getAttribute('role') || '',
                        }};
                        chain.push(info);
                        if (el.onclick || el.getAttribute('onclick') ||
                            el.tagName === 'A' || el.tagName === 'BUTTON' ||
                            el.getAttribute('role') === 'button') {{
                            return JSON.stringify({{found: true, chain: chain}});
                        }}
                        el = el.parentElement;
                    }}
                    return JSON.stringify({{found: false, chain: chain}});
                }}
            }}
            return JSON.stringify({{found: false, chain: [], error: 'text not found'}});
        """, kw)
        log(f'  [{kw}]: {result}')

    # ── 4. Dump HTML of status section ────────────────────────────────────────
    log()
    log('=' * 70)
    log('STATUS SECTION HTML (first 5000 chars):')
    status_html = driver.execute_script("""
        // Try multiple selectors for the status content area
        var selectors = [
            '#tabStatus', '.tabContent', '[id*="Status"]',
            '[class*="workflow"]', '[class*="task"]',
            'table', 'ul', 'ol',
        ];
        for (var s of selectors) {
            var el = document.querySelector(s);
            if (el && el.innerHTML && el.innerHTML.length > 200) {
                return '/* selector: ' + s + ' */\\n' + el.outerHTML.substring(0, 5000);
            }
        }
        // Fallback: area after "Status" heading
        var headings = document.querySelectorAll('h2, h3, h4, strong');
        for (var h of headings) {
            if (h.textContent.trim() === 'Status') {
                var parent = h.parentElement;
                if (parent) return '/* h_parent */\\n' + parent.outerHTML.substring(0, 5000);
            }
        }
        return 'NO SECTION FOUND';
    """)
    log(status_html[:6000])

    # ── 5. All <a> elements on the Status tab ─────────────────────────────────
    log()
    log('=' * 70)
    log('ALL <a> ELEMENTS ON STATUS TAB:')
    links_info = driver.execute_script("""
        var result = [];
        var links = document.querySelectorAll('a');
        for (var i = 0; i < links.length; i++) {
            var l = links[i];
            if (l.offsetParent !== null) {  // visible only
                result.push({
                    text: l.textContent.trim().substring(0, 60),
                    href: (l.getAttribute('href') || '').substring(0, 100),
                    onclick: (l.getAttribute('onclick') || '').substring(0, 100),
                    id: l.id,
                    cls: l.className.toString().substring(0, 60),
                });
            }
        }
        return JSON.stringify(result);
    """)
    try:
        for lnk in json.loads(links_info):
            if lnk['text'] or lnk['onclick']:
                log(f"  text='{lnk['text']}' href='{lnk['href']}' onclick='{lnk['onclick']}' class='{lnk['cls']}'")
    except Exception as e:
        log(f'Parse error: {e}\nRaw: {links_info[:1000]}')

    # ── 6. Click "Complaint Intake" (whatever element has the text) ──────────
    log()
    log('=' * 70)
    log('ATTEMPTING CLICK ON "Complaint Intake" row and wait 5s...')
    pre_text = driver.find_element(By.TAG_NAME, 'body').text
    clicked = driver.execute_script("""
        var walker = document.createTreeWalker(
            document.body, NodeFilter.SHOW_TEXT, null, false
        );
        var node;
        while (node = walker.nextNode()) {
            if (node.textContent.trim() === 'Complaint Intake') {
                var el = node.parentElement;
                for (var i = 0; i < 10; i++) {
                    if (!el) break;
                    if (el.tagName === 'A' || el.tagName === 'BUTTON' ||
                        el.getAttribute('onclick') || el.getAttribute('role') === 'button') {
                        el.click();
                        return 'clicked: ' + el.tagName + ' | ' + el.outerHTML.substring(0, 200);
                    }
                    if (el.tagName === 'TR' || el.tagName === 'LI') {
                        el.click();
                        return 'clicked row: ' + el.tagName + ' | ' + el.outerHTML.substring(0, 200);
                    }
                    el = el.parentElement;
                }
                return 'no clickable ancestor found, clicked parent: ' + node.parentElement.outerHTML.substring(0,200);
            }
        }
        return 'text not found';
    """)
    log(f'Click result: {clicked}')
    time.sleep(5)

    post_text = driver.find_element(By.TAG_NAME, 'body').text
    if post_text != pre_text:
        # Find what's new
        pre_lines = set(pre_text.split('\n'))
        post_lines = post_text.split('\n')
        new_lines = [l for l in post_lines if l not in pre_lines and l.strip()]
        log('NEW CONTENT after click:')
        for l in new_lines[:30]:
            log(f'  + {l}')
    else:
        log('NO CHANGE in page text after click')

    # ── 7. Inspections tab + View Details delta approach ─────────────────────
    log()
    log('=' * 70)
    log('INSPECTIONS TAB - View Details delta approach...')
    driver.get(TEST_URL)
    time.sleep(8)
    click_tab(driver, 'Inspection')
    time.sleep(4)

    log('Inspections visible text:')
    insp_text = driver.find_element(By.TAG_NAME, 'body').text
    log(insp_text[:800])

    # Find View Details links
    vd_links = driver.find_elements(By.PARTIAL_LINK_TEXT, 'View Details')
    log(f'\nView Details links: {len(vd_links)}')
    for i, vd in enumerate(vd_links):
        log(f'  [{i}] text="{vd.text}" href="{vd.get_attribute("href")}" onclick="{vd.get_attribute("onclick")}"')

    if vd_links:
        log()
        log('Clicking first View Details (delta approach)...')
        pre_vd = driver.find_element(By.TAG_NAME, 'body').text
        pre_url = driver.current_url
        driver.execute_script("arguments[0].click();", vd_links[0])
        time.sleep(4)

        post_url = driver.current_url
        post_vd = driver.find_element(By.TAG_NAME, 'body').text
        log(f'URL before: {pre_url}')
        log(f'URL after:  {post_url}')
        log(f'Text length before: {len(pre_vd)} | after: {len(post_vd)}')

        # Find new content
        pre_set = set(l.strip() for l in pre_vd.split('\n') if l.strip())
        new_content = [l for l in post_vd.split('\n') if l.strip() and l.strip() not in pre_set]
        log('NEW CONTENT after View Details click:')
        for l in new_content[:50]:
            log(f'  + {l}')

        # Also look for Result Comments pattern
        rc_idx = post_vd.find('Result Comments')
        if rc_idx >= 0:
            log(f'\nResult Comments found at index {rc_idx}:')
            log(post_vd[rc_idx:rc_idx+500])
        else:
            log('Result Comments NOT found in post-click text')

        # Look at what HTML was added to the body
        log()
        log('DOM changes — elements NOT previously visible:')
        dom_new = driver.execute_script("""
            var divs = document.querySelectorAll('div, section, article, [role="dialog"]');
            var result = [];
            for (var d of divs) {
                if (d.offsetParent !== null) {
                    var txt = d.textContent.trim();
                    if (txt.includes('Result') || txt.includes('Comment') ||
                        txt.includes('Inspection') || txt.includes('Inspector')) {
                        if (txt.length < 2000 && txt.length > 20) {
                            result.push({
                                tag: d.tagName,
                                id: d.id,
                                cls: d.className.toString().substring(0, 60),
                                text: txt.substring(0, 300),
                                html: d.outerHTML.substring(0, 400),
                            });
                            if (result.length >= 8) break;
                        }
                    }
                }
            }
            return JSON.stringify(result);
        """)
        try:
            for item in json.loads(dom_new):
                log(f"\n  tag={item['tag']} id='{item['id']}' cls='{item['cls']}'")
                log(f"  text: {item['text'][:200]}")
                log(f"  html: {item['html'][:300]}")
        except Exception as e:
            log(f'DOM parse error: {e}\n{dom_new[:500]}')

finally:
    driver.quit()
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\nSaved to {OUT_FILE}')
