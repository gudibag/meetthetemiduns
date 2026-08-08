# #MeetTheTemiduns — Registry Setup Guide

Your registry is already built into `MeetTheTemiduns.html`. It needs one backend — a Google Sheet + Apps Script — which also powers your RSVP form. About 15 minutes, one-time.

## Step 1 — Create the sheet
1. Upload `MeetTheTemiduns_Registry_Sheet.xlsx` to Google Drive and open it with **Google Sheets** (or copy its tabs into a new Google Sheet).
2. You'll have four tabs: **READ ME, Registry, Pledges, RSVPs**.

## Step 2 — Add the script
1. In the sheet: **Extensions → Apps Script**.
2. Delete the placeholder code, paste everything from `Registry_AppsScript_Code.gs`, **Save**.

## Step 3 — Deploy as a Web App
1. **Deploy → New deployment** → type **Web app**.
2. **Execute as:** Me. **Who has access:** Anyone. **Deploy**.
3. Authorise when prompted (pick your account → Advanced → Go to project → Allow).
4. **Copy the Web App URL.**

## Step 4 — Connect the website
In `MeetTheTemiduns.html`, find this line and paste your URL:
```js
const REGISTRY_URL = 'PASTE_YOUR_WEB_APP_URL_HERE';
```
Also replace every `[BANK ACCOUNT NUMBER]` with your real GTBank number.

## Step 5 — Publish
Commit the edited `MeetTheTemiduns.html` (renamed `index.html`) to your GitHub repo. Done.

---

## Running it day-to-day (confirm-first — anti-abuse)
- **Add/remove gifts:** edit the **Registry** tab. Changes appear on a refresh.
- **A pledge comes in:** it lands in **Pledges** as **Pending** — private to you, and **invisible on the site**.
- **You confirm payment:** when the GTBank alert matches, set **Confirmed = Yes**. *This is the only thing that moves the public bar.*
- **Result:** a bad actor can submit fake pledges endlessly; nothing shows publicly until real money is confirmed by you.
- **Guests see:** only confirmed anonymous totals + "Blessed ✓". Never names, amounts, or pending pledges.

## If you redeploy the script later
Use **Deploy → Manage deployments → Edit (pencil) → New version** so the URL stays the same.
