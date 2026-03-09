"""
STLCA Seattle Services Portal Scraper — v4
Targets the STATUS TAB of each complaint record.

Extracts the full workflow timeline:
  Each step (Complaint Intake, Initial Investigation, NOV, Resolution, Closed)
  with: Due date | Assigned to | Marked as | Marked on date

Two output files:
  portal_scrape_workflow.csv  — one row per workflow STEP (for delay analysis)
  portal_scrape_results.csv   — one row per RECORD (summary/key fields flattened)

Log: SCRIPTS/scraper_run_log.txt

Run from stlca_web root:
  python SCRIPTS/portal_scraper.py
"""

import os
import re
import sys
import time
import logging
import traceback

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ── PATHS ────────────────────────────────────────────────────────────────────
ROOT          = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS_CSV   = os.path.join(ROOT, 'SCRIPTS', 'scraper_targets.csv')
OUTPUT_CSV    = os.path.join(ROOT, 'SCRIPTS', 'portal_scrape_results.csv')
WORKFLOW_CSV  = os.path.join(ROOT, 'SCRIPTS', 'portal_scrape_workflow.csv')
LOG_FILE      = os.path.join(ROOT, 'SCRIPTS', 'scraper_run_log.txt')

# ── CONFIG ───────────────────────────────────────────────────────────────────
BASE_URL   = 'https://services.seattle.gov/portal/customize/LinkToRecord.aspx?altId={record_num}&RecordGroup=1'
PAGE_WAIT  = 12
JS_SETTLE  = 4
PAUSE      = 3
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)s  %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger(__name__)


# ── REGEX PATTERNS for Status tab text ───────────────────────────────────────
# "Due on 09/09/2025, assigned to Stephen Rudolph"
RE_DUE     = re.compile(r'Due on\s+(\d{1,2}/\d{1,2}/\d{4}),?\s+assigned to\s+(.+)', re.IGNORECASE)
# "Marked as Intake Completed on 09/09/2025"
RE_MARKED  = re.compile(r'Marked as\s+(.+?)\s+on\s+(\d{1,2}/\d{1,2}/\d{4})', re.IGNORECASE)
# ─────────────────────────────────────────────────────────────────────────────


def make_driver():
    opts = Options()
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_argument('--disable-popup-blocking')   # allow showInspectionPopupDialog windows
    opts.add_experimental_option('excludeSwitches', ['enable-automation'])
    opts.add_experimental_option('useAutomationExtension', False)
    # Allow all popups via Chrome prefs
    prefs = {'profile.default_content_settings.popups': 1}
    opts.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )
    driver.set_window_size(1400, 900)
    return driver


def wait_ready(driver, timeout=PAGE_WAIT):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
    except Exception:
        pass
    time.sleep(JS_SETTLE)


def click_tab(driver, label):
    """Click the named tab. Returns True on success."""
    # Accela tabs: <a> elements in a tab nav bar
    candidates = [
        'a[role="tab"]',
        '.nav-tabs a',
        '.tab-links a',
        '#tabstrip a',
        '.tabList a',
        'a',
    ]
    for sel in candidates:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            for el in els:
                if label.lower() in el.text.strip().lower() and el.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView(true);", el)
                    time.sleep(0.3)
                    driver.execute_script("arguments[0].click();", el)
                    time.sleep(2.5)
                    log.info(f'    Clicked tab: "{el.text.strip()}"')
                    return True
        except Exception:
            pass
    return False


def get_body_text(driver):
    """Full page text via BeautifulSoup (captures hidden DOM elements)."""
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()
        return soup.get_text(separator='\n', strip=True)
    except Exception:
        try:
            return driver.find_element(By.TAG_NAME, 'body').text
        except Exception:
            return ''


def get_visible_text(driver):
    """Visible text only — what you'd actually see on screen."""
    try:
        return driver.find_element(By.TAG_NAME, 'body').text
    except Exception:
        return ''


def force_show_hidden(driver):
    """
    JS: Make all hidden/collapsed elements visible so their text is readable.
    Handles both inline style="display:none" and CSS class-based hiding.
    """
    try:
        driver.execute_script("""
            var all = document.querySelectorAll('*');
            for (var i = 0; i < all.length; i++) {
                var el = all[i];
                var st = window.getComputedStyle(el);
                if (st.display === 'none' || st.visibility === 'hidden') {
                    el.style.display = 'block';
                    el.style.visibility = 'visible';
                }
            }
        """)
        time.sleep(0.5)
    except Exception:
        pass


def click_expand_buttons(driver):
    """
    Click every workflow step expand button on the Status tab.

    DOM probe confirmed: expand buttons are <a href="javascript:void(0)"
    onclick="ControlDisplay($get('GUID'), $get('img_GUID'))" class="NotShowLoading">
    Select them with: a[onclick*="ControlDisplay"]

    Each click triggers an AJAX load of the step detail panel — wait between clicks.
    """
    try:
        expand_links = driver.find_elements(By.CSS_SELECTOR, "a[onclick*='ControlDisplay']")
        log.info(f'    ControlDisplay expand buttons found: {len(expand_links)}')
        for i, link in enumerate(expand_links):
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", link)
                driver.execute_script("arguments[0].click();", link)
                time.sleep(2)  # AJAX needs time per click
                log.info(f'    Clicked expand button [{i+1}/{len(expand_links)}]')
            except Exception as e:
                log.warning(f'    Expand button [{i+1}] error: {e}')
    except Exception as e:
        log.warning(f'    click_expand_buttons error: {e}')

    time.sleep(1)


PORTAL_BASE = 'https://services.seattle.gov'

def scrape_inspection_details(driver):
    """
    Fetch each inspection's View Details page to extract Result Comments.

    showInspectionPopupDialog() opens a popup window that Chrome blocks.
    Fix: extract the URL from the onclick attribute, navigate to it directly
    in the main window, read the content, then navigate back.

    URL pattern from onclick:
      showInspectionPopupDialog('/Portal/Inspection/InspectionDetails.aspx?...&isPopup=Y&ID=XXXXX', ...)

    Returns list of detail dicts with result_comments and status_history.
    """
    details = []

    # Find all View Details links
    try:
        links = driver.find_elements(By.PARTIAL_LINK_TEXT, 'View Details')
    except Exception:
        links = []

    if not links:
        try:
            links = driver.find_elements(By.CSS_SELECTOR,
                "a[onclick*='showInspectionPopupDialog'], a[onclick*='InspectionDetails']")
        except Exception:
            links = []

    log.info(f'    View Details links found: {len(links)}')

    return_url = driver.current_url

    # Collect all onclick URLs first (before any navigation stales the elements)
    detail_urls = []
    for link in links:
        try:
            onclick = link.get_attribute('onclick') or ''
            href    = link.get_attribute('href') or ''
            popup_url = ''
            m = re.search(r"showInspectionPopupDialog\('([^']+)'", onclick)
            if m:
                path = m.group(1)
                # Strip isPopup=Y so it loads as a standalone page
                path = re.sub(r'[&?]isPopup=Y', '', path)
                popup_url = PORTAL_BASE + path if path.startswith('/') else path
            elif 'InspectionDetails' in href:
                popup_url = re.sub(r'[&?]isPopup=Y', '', href)
            if popup_url:
                detail_urls.append(popup_url)
            else:
                log.warning(f'    View Details: no URL in onclick/href. onclick={onclick[:150]}')
        except Exception as e:
            log.warning(f'    View Details URL extract error: {e}')

    log.info(f'    Detail URLs collected: {len(detail_urls)}')

    # Log all iframes currently on the page BEFORE any clicks (baseline)
    baseline_frames = driver.execute_script("""
        var iframes = document.querySelectorAll('iframe');
        var srcs = [];
        for (var f of iframes) { srcs.push(f.src || f.getAttribute('src') || ''); }
        return srcs;
    """)
    log.info(f'    Baseline iframes on page: {baseline_frames}')

    for i, detail_url in enumerate(detail_urls):
        try:
            log.info(f'    View Details [{i+1}/{len(detail_urls)}]')

            # Click the View Details link — showInspectionPopupDialog injects an iframe overlay
            fresh_links = driver.find_elements(By.PARTIAL_LINK_TEXT, 'View Details')
            if i < len(fresh_links):
                driver.execute_script("arguments[0].click();", fresh_links[i])
            time.sleep(5)  # allow the overlay iframe to be injected and loaded

            # Find ALL iframes now — look for ones with InspectionDetails in src
            all_frame_srcs = driver.execute_script("""
                var iframes = document.querySelectorAll('iframe');
                var result = [];
                for (var f of iframes) {
                    result.push({
                        src: f.src || f.getAttribute('src') || '',
                        id: f.id || '',
                        cls: f.className || '',
                        visible: f.offsetParent !== null,
                    });
                }
                return result;
            """)
            log.info(f'    All iframes after click ({len(all_frame_srcs)}): {all_frame_srcs}')

            popup_text = ''
            # Find the InspectionDetails iframe by src
            insp_frame_idx = None
            for fi, finfo in enumerate(all_frame_srcs):
                if 'InspectionDetails' in finfo.get('src', '') or \
                   'Inspection' in finfo.get('src', ''):
                    insp_frame_idx = fi
                    log.info(f'    Found InspectionDetails iframe at index {fi}: {finfo}')
                    break

            if insp_frame_idx is not None:
                # ACADialogFrame is always the inspection overlay iframe.
                # Read via JS contentDocument at 1s — before the portal redirect fires.
                time.sleep(1)
                js_text = driver.execute_script("""
                    var iframe = document.getElementById('ACADialogFrame');
                    if (!iframe) return 'NO_IFRAME';
                    try {
                        var doc = iframe.contentDocument || iframe.contentWindow.document;
                        if (!doc || !doc.body) return 'NO_BODY';
                        return doc.body.innerText || doc.body.textContent || 'EMPTY';
                    } catch(e) {
                        return 'JS_ERR:' + e.message;
                    }
                """)
                popup_text = str(js_text) if js_text else ''
                log.info(f'    ACADialogFrame JS read ({len(popup_text)} chars): {popup_text[:400]}')

                # Dismiss the overlay so subsequent View Details clicks work
                try:
                    driver.execute_script("""
                        var close = document.querySelector(
                            '.ACA_Dialog_Closes a, .ACA_Dialog_Close, [id*="Close"], [title="Close"]'
                        );
                        if (close) { close.click(); }
                        else {
                            // Hide overlay divs directly
                            var overlay = document.querySelector('.mask_iframe, .ACA_Dialog');
                            if (overlay) overlay.style.display = 'none';
                            var frame = document.getElementById('ACADialogFrame');
                            if (frame) frame.src = 'about:blank';
                        }
                    """)
                    time.sleep(0.5)
                except Exception:
                    pass
            else:
                # No InspectionDetails iframe found — try ALL non-baseline iframes
                log.warning('    No InspectionDetails iframe found — trying new iframes')
                all_iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                for fi, frame_el in enumerate(all_iframes):
                    try:
                        frame_src = frame_el.get_attribute('src') or ''
                        if frame_src in baseline_frames:
                            continue  # skip baseline iframes
                        driver.switch_to.frame(frame_el)
                        time.sleep(2)
                        ft = get_body_text(driver)
                        driver.switch_to.default_content()
                        if len(ft) > 100:
                            popup_text = ft
                            log.info(f'    New iframe [{fi}] content ({len(ft)} chars): {ft[:300]}')
                            break
                    except Exception:
                        driver.switch_to.default_content()

            detail = {
                'index': i + 1,
                'popup_url': detail_url[:300],
                'modal_text': popup_text[:2000],
                'result_comments': '',
                'status_history': '',
                'last_updated': '',
            }

            rc_idx = popup_text.find('Result Comments')
            if rc_idx >= 0:
                detail['result_comments'] = popup_text[rc_idx:rc_idx + 800]

            sh_idx = popup_text.find('Status History')
            if sh_idx >= 0:
                detail['status_history'] = popup_text[sh_idx:sh_idx + 600]

            m = re.search(r'Last updated\s+(.+?\d{2}:\d{2}\s*[AP]M)', popup_text)
            if m:
                detail['last_updated'] = m.group(1).strip()

            details.append(detail)

        except Exception as e:
            log.warning(f'    View Details [{i+1}] error: {e}')

    # Navigate back to the inspections page after all detail URLs are fetched
    try:
        driver.get(return_url)
        time.sleep(3)
    except Exception:
        pass

    return details


def scrape_related_records(driver):
    """
    Read the Related Records tab table.
    Returns list of {record_num, record_type, date, link} dicts.
    """
    records = []
    try:
        # Find all table rows in the related records section
        rows = driver.find_elements(By.CSS_SELECTOR, 'table tr, .record-list tr')
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 2:
                rec = {
                    'record_num': cells[0].text.strip() if cells else '',
                    'record_type': cells[1].text.strip() if len(cells) > 1 else '',
                    'date': cells[2].text.strip() if len(cells) > 2 else '',
                }
                if rec['record_num'] and rec['record_num'] != 'Record Number':
                    records.append(rec)
    except Exception:
        pass
    return records


def parse_workflow_steps(body_text):
    """
    Parse the Status tab workflow timeline into structured steps.

    BeautifulSoup splits the portal's DOM into one token per line, so the
    "Due on DATE, assigned to NAME / Marked as STATUS on DATE" pattern
    actually looks like:

        Complaint Intake
        Due on
        02/28/2019
        , assigned to
        TBD
        Marked as
        Intake Completed
        on
        02/28/2019

    This function uses a line-by-line state machine to handle that format.
    Returns list of dicts: step_name, due_date, assigned_to, marked_as, marked_on
    """
    STEP_NAMES = {
        'complaint intake', 'initial construction investigation',
        'initial hzn investigation', 'initial hzw investigation',
        'initial noise investigation', 'initial pota investigation',
        'initial investigation', 'pre-nov actions', 'pre-nov',
        'issue nov/eo', 'issue nov', 'follow-up investigation',
        'follow-up investigation - nov', 'prep to close',
        'complaint resolution', 'feedback', 'closed',
    }
    DATE_RE = re.compile(r'^\d{1,2}/\d{1,2}/\d{4}$')

    lines = [l.strip() for l in body_text.splitlines() if l.strip()]
    steps = []

    current_step   = None
    pending_due    = ''
    pending_assign = ''

    # State machine states
    STATE_IDLE      = 'idle'
    STATE_IN_STEP   = 'in_step'
    STATE_GOT_DUE   = 'got_due'        # saw "Due on"
    STATE_GOT_DATE  = 'got_date'       # captured date after "Due on"
    STATE_GOT_ASSK  = 'got_assk'       # saw ", assigned to"
    STATE_MRKD_KW   = 'marked_kw'      # saw "Marked as"
    STATE_MRKD_ST   = 'marked_status'  # captured status after "Marked as"
    STATE_MRKD_ON   = 'marked_on'      # saw "on" after status

    state      = STATE_IDLE
    tmp_due    = ''
    tmp_assign = ''
    tmp_status = ''

    for line in lines:
        ll = line.lower()

        # ── Check for step name transition (only when not mid-token) ──────
        # Must NOT interrupt STATE_MRKD_KW/ST/ON — "Closed" is both step name
        # and a valid status value; without this guard the parser resets prematurely.
        safe_for_step = state in (STATE_IDLE, STATE_IN_STEP, STATE_GOT_DATE)
        clean = re.sub(r'^[✓✗►▼▸\-\s]+', '', line).strip()
        if safe_for_step and clean.lower() in STEP_NAMES:
            current_step = clean
            state = STATE_IN_STEP
            tmp_due = tmp_assign = tmp_status = ''
            pending_due = pending_assign = ''
            continue

        if current_step is None:
            continue

        # ── State machine ─────────────────────────────────────────────────
        if state in (STATE_IN_STEP, STATE_GOT_DATE):
            if ll == 'due on':
                state = STATE_GOT_DUE
                tmp_due = ''
                continue

            if ll == 'marked as':
                state = STATE_MRKD_KW
                tmp_status = ''
                continue

        if state == STATE_GOT_DUE:
            if DATE_RE.match(line):
                tmp_due = line
                state = STATE_GOT_DATE
            continue

        if state == STATE_GOT_DATE:
            if ', assigned to' in ll or ll == ', assigned to':
                state = STATE_GOT_ASSK
            elif ll == 'marked as':
                pending_due = tmp_due
                state = STATE_MRKD_KW
                tmp_status = ''
            elif ll == 'due on':
                pending_due = tmp_due
                state = STATE_GOT_DUE
                tmp_due = ''
            continue

        if state == STATE_GOT_ASSK:
            # Next non-empty line is the assigned-to name
            tmp_assign = line
            pending_due = tmp_due
            pending_assign = tmp_assign
            state = STATE_IN_STEP
            continue

        if state == STATE_MRKD_KW:
            # Next line is the status string
            tmp_status = line
            state = STATE_MRKD_ST
            continue

        if state == STATE_MRKD_ST:
            if ll == 'on':
                state = STATE_MRKD_ON
            continue

        if state == STATE_MRKD_ON:
            if DATE_RE.match(line):
                steps.append({
                    'step_name':   current_step,
                    'due_date':    pending_due,
                    'assigned_to': pending_assign,
                    'marked_as':   tmp_status,
                    'marked_on':   line,
                })
                # Reset for next sub-item in same step
                pending_due = pending_assign = ''
                tmp_due = tmp_assign = tmp_status = ''
                state = STATE_IN_STEP
            continue

    return steps


def flatten_steps(steps, record_num):
    """
    Flatten workflow steps into a single-row dict for the summary CSV.
    Priority fields:
      - intake_date, intake_assigned, intake_marked_as
      - initial_invest_date, initial_invest_assigned, initial_invest_marked_as
      - nov_issued_date, nov_marked_as
      - followup_date, followup_assigned, followup_marked_as
      - resolution_marked_as, resolution_date
      - closed_date
    """
    def find_step(keywords):
        for s in steps:
            if any(k.lower() in s['step_name'].lower() for k in keywords):
                return s
        return {}

    intake     = find_step(['intake'])
    invest     = find_step(['initial', 'investigation'])
    nov        = find_step(['nov', 'issue'])
    followup   = find_step(['follow'])
    resolution = find_step(['resolution'])
    closed     = find_step(['closed'])

    return {
        'record_num':           record_num,
        'step_count':           len(steps),
        'intake_date':          intake.get('due_date', ''),
        'intake_marked_date':   intake.get('marked_on', ''),
        'intake_assigned':      intake.get('assigned_to', ''),
        'intake_marked_as':     intake.get('marked_as', ''),
        'invest_step':          invest.get('step_name', ''),
        'invest_date':          invest.get('due_date', ''),
        'invest_marked_date':   invest.get('marked_on', ''),
        'invest_assigned':      invest.get('assigned_to', ''),
        'invest_marked_as':     invest.get('marked_as', ''),
        'nov_date':             nov.get('due_date', ''),
        'nov_marked_date':      nov.get('marked_on', ''),
        'nov_marked_as':        nov.get('marked_as', ''),
        'followup_date':        followup.get('due_date', ''),
        'followup_marked_date': followup.get('marked_on', ''),
        'followup_assigned':    followup.get('assigned_to', ''),
        'followup_marked_as':   followup.get('marked_as', ''),
        'resolution_date':      resolution.get('due_date', ''),
        'resolution_marked_date': resolution.get('marked_on', ''),
        'resolution_assigned':  resolution.get('assigned_to', ''),
        'resolution_marked_as': resolution.get('marked_as', ''),
        'closed_date':          closed.get('marked_on', ''),
    }


def scrape_record(driver, record_num, link, case_name, address, orig_status):
    log.info(f'\n{"="*60}')
    log.info(f'  {record_num} | {case_name} | {address}')
    log.info(f'{"="*60}')

    result = {
        'record_num':           record_num,
        'case_name':            case_name,
        'address':              address,
        'original_status':      orig_status,
        'url_used':             '',
        'page_title':           '',
        'record_status':        '',
        'complaint_description':'',
        'status_tab_raw':       '',
        'inspections_raw':      '',
        'inspection_comments':  '',
        'related_records_raw':  '',
        'error':                '',
    }
    workflow_rows = []

    try:
        url = BASE_URL.format(record_num=record_num)
        if pd.notna(link) and 'http' in str(link):
            url = str(link).strip()
        result['url_used'] = url

        # ── 1. Load record page (Record Details tab) ─────────────────────────
        driver.get(url)
        wait_ready(driver)
        result['page_title'] = driver.title[:200]
        log.info(f'  Loaded: {result["page_title"][:80]}')

        body = get_body_text(driver)
        m = re.search(r'What is your complaint\??\s*:?\s*\n(.+)', body)
        if m:
            result['complaint_description'] = m.group(1).strip()[:400]
        m2 = re.search(r'Record Status:\s*(.+)', body)
        if m2:
            result['record_status'] = m2.group(1).strip()[:100]

        # ── 2. STATUS TAB ────────────────────────────────────────────────────
        log.info('  Clicking Status tab...')
        status_clicked = click_tab(driver, 'Status')
        if not status_clicked:
            log.warning('  Status tab click failed — trying hash URL')
            driver.get(url.split('#')[0] + '#tabStatus')
        time.sleep(5)  # Accela AJAX needs time

        # Log visible page state BEFORE expanding
        visible_pre = get_visible_text(driver)
        log.info(f'  Status tab visible text ({len(visible_pre)} chars) PRE-expand:')
        log.info(f'  {visible_pre[:600]}')
        log.info('  ---')

        # Click all ControlDisplay expand buttons to load step detail panels (AJAX)
        click_expand_buttons(driver)
        time.sleep(2)

        # Capture full text (BS4 parses hidden DOM too)
        status_text = get_body_text(driver)
        result['status_tab_raw'] = status_text[:10000]
        log.info(f'  Status tab BS4 text ({len(status_text)} chars) POST-expand:')
        log.info(f'  {status_text[:800]}')
        log.info('  ---')

        # Parse + record workflow steps
        steps = parse_workflow_steps(status_text)
        log.info(f'  Workflow steps parsed: {len(steps)}')
        for s in steps:
            log.info(f'    STEP: {s["step_name"]:<35} | {s["assigned_to"]:<20} | {s["marked_as"]} on {s["marked_on"]}')
            workflow_rows.append({'record_num': record_num, 'case_name': case_name,
                                  'address': address, **s})
        result.update(flatten_steps(steps, record_num))

        # ── 3. INSPECTIONS & APPOINTMENTS TAB ───────────────────────────────
        log.info('  Navigating back to record page for Inspections tab...')
        driver.get(url)
        wait_ready(driver)

        log.info('  Clicking Inspections tab...')
        insp_clicked = click_tab(driver, 'Inspection')
        if insp_clicked:
            time.sleep(4)
            insp_text = get_visible_text(driver)
            result['inspections_raw'] = insp_text[:5000]
            log.info(f'  Inspections tab visible ({len(insp_text)} chars):')
            log.info(f'  {insp_text[:500]}')
            log.info('  ---')

            # Click View Details on each inspection to get Result Comments
            insp_details = scrape_inspection_details(driver)
            if insp_details:
                all_comments = []
                for d in insp_details:
                    rc = d.get('result_comments', d.get('modal_text', ''))
                    if rc:
                        all_comments.append(rc[:400])
                result['inspection_comments'] = ' || '.join(all_comments)
                log.info(f'  Inspection comments captured: {len(all_comments)} modals')
        else:
            log.info('  Inspections tab: not found/clickable')

        # ── 4. RELATED RECORDS TAB ───────────────────────────────────────────
        log.info('  Clicking Related Records tab...')
        rel_clicked = click_tab(driver, 'Related Records')
        if rel_clicked:
            time.sleep(3)
            rel_text = get_visible_text(driver)
            result['related_records_raw'] = rel_text[:3000]
            log.info(f'  Related Records ({len(rel_text)} chars): {rel_text[:300]}')
        else:
            log.info('  Related Records tab: not found/clickable')

        log.info(f'  DONE: {record_num}')

    except Exception as e:
        result['error'] = traceback.format_exc()[:800]
        log.error(f'  ERROR on {record_num}: {e}')

    return result, workflow_rows


def main():
    log.info('=' * 60)
    log.info('STLCA Portal Scraper v4 — ControlDisplay expand + popup window fix')
    log.info('=' * 60)
    log.info(f'Targets: {TARGETS_CSV}')
    log.info(f'Summary output: {OUTPUT_CSV}')
    log.info(f'Workflow output: {WORKFLOW_CSV}')

    if not os.path.exists(TARGETS_CSV):
        log.error(f'TARGETS CSV NOT FOUND: {TARGETS_CSV}')
        sys.exit(1)

    targets = pd.read_csv(TARGETS_CSV).drop_duplicates(subset='RecordNum')
    log.info(f'Records to scrape: {len(targets)}\n')

    driver = make_driver()
    all_results  = []
    all_workflow = []

    try:
        for idx, row in enumerate(targets.itertuples(), 1):
            rec    = row.RecordNum
            link   = getattr(row, 'Link', '')
            case   = getattr(row, 'Case', '')
            addr   = getattr(row, 'Address', '')
            status = getattr(row, 'Status', '')

            log.info(f'[{idx}/{len(targets)}] {case} | {rec}')

            result, wf_rows = scrape_record(driver, rec, link, case, addr, status)
            all_results.append(result)
            all_workflow.extend(wf_rows)

            # Save incrementally
            pd.DataFrame(all_results).to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
            pd.DataFrame(all_workflow).to_csv(WORKFLOW_CSV, index=False, encoding='utf-8')
            log.info(f'  Saved: {len(all_results)} records, {len(all_workflow)} workflow rows')

            time.sleep(PAUSE)

    except KeyboardInterrupt:
        log.info('Stopped by user.')
    finally:
        driver.quit()

    # Final save
    pd.DataFrame(all_results).to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
    pd.DataFrame(all_workflow).to_csv(WORKFLOW_CSV, index=False, encoding='utf-8')

    log.info('\n' + '=' * 60)
    log.info('FINAL SUMMARY')
    log.info('=' * 60)
    log.info(f'Records scraped:    {len(all_results)}')
    log.info(f'Workflow steps:     {len(all_workflow)}')
    log.info(f'Summary CSV:        {OUTPUT_CSV}')
    log.info(f'Workflow CSV:       {WORKFLOW_CSV}')

    df = pd.DataFrame(all_results)
    for r in df.itertuples():
        log.info(
            f"{r.record_num:25} "
            f"steps={r.step_count if hasattr(r,'step_count') else '?':>3} "
            f"intake={r.intake_date if hasattr(r,'intake_date') else '':12} "
            f"closed={r.closed_date if hasattr(r,'closed_date') else '':12} "
            f"resolution={r.resolution_marked_as[:20] if hasattr(r,'resolution_marked_as') and r.resolution_marked_as else 'n/a':20} "
            f"err={'Y' if r.error else 'n'}"
        )


if __name__ == '__main__':
    main()
