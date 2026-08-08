/**
 * #MeetTheTemiduns — Wedding Registry + RSVP backend
 * ---------------------------------------------------
 * Single Apps Script serving three actions:
 *   ?action=registry   -> public: items + ANONYMOUS pledged totals
 *   POST (pledge)       -> logs a private pledge row
 *   POST (rsvp)         -> logs an RSVP row (with duplicate-email guard)
 *
 * PRIVACY: the public 'registry' response returns only the SUM pledged
 * per item. Individual giver names/amounts never leave the sheet.
 */

// ---- CONFIG -----------------------------------------------------------------
var SHEET_ID = '';            // leave '' if the script is bound to the sheet
var REGISTRY_TAB = 'Registry';
var PLEDGES_TAB  = 'Pledges';
var RSVP_TAB     = 'RSVPs';

function ss_() {
  return SHEET_ID ? SpreadsheetApp.openById(SHEET_ID)
                  : SpreadsheetApp.getActiveSpreadsheet();
}
function tab_(name) {
  var s = ss_().getSheetByName(name);
  if (!s) { s = ss_().insertSheet(name); }
  return s;
}
function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

// ---- GET: serve registry with anonymous totals ------------------------------
function doGet(e) {
  var action = (e && e.parameter && e.parameter.action) || 'registry';
  if (action === 'registry') return json_(getRegistry_());
  return json_({ status: 'error', message: 'unknown action' });
}

function getRegistry_() {
  var reg = tab_(REGISTRY_TAB);
  var pled = tab_(PLEDGES_TAB);

  // Registry rows -> items
  var rv = reg.getDataRange().getValues();
  var items = [];
  // header row assumed: Item | Description | Category | Goal | Emoji | Active
  for (var i = 1; i < rv.length; i++) {
    var r = rv[i];
    if (!r[0]) continue;
    var active = (r[5] === '' || r[5] === true ||
                  String(r[5]).toLowerCase() === 'yes' ||
                  String(r[5]).toLowerCase() === 'true');
    if (!active) continue;
    items.push({
      item: String(r[0]),
      description: String(r[1] || ''),
      category: String(r[2] || ''),
      goal: Number(r[3]) || 0,
      emoji: String(r[4] || '🎁'),
      pledged: 0
    });
  }

  // Sum CONFIRMED + pending pledges per item (anonymous)
  var pv = pled.getDataRange().getValues();
  // header: Timestamp | Item | Giver | Amount | Ref | Confirmed
  // PUBLIC total counts CONFIRMED pledges only (col 6 = 'Yes').
  // Unconfirmed pledges stay private and invisible until you verify payment.
  var totals = {};
  for (var j = 1; j < pv.length; j++) {
    var it = String(pv[j][1] || '');
    var amt = Number(pv[j][3]) || 0;
    var conf = String(pv[j][5] || '').toLowerCase();
    if (!it) continue;
    if (conf !== 'yes' && conf !== 'true' && conf !== 'confirmed') continue;
    totals[it] = (totals[it] || 0) + amt;
  }
  items.forEach(function(x){ x.pledged = totals[x.item] || 0; });

  // Public summary (no names, no amounts per person)
  var totalGoal = 0, totalPledged = 0, blessed = 0;
  items.forEach(function(x){
    totalGoal += x.goal; totalPledged += x.pledged;
    if (x.pledged >= x.goal && x.goal > 0) blessed++;
  });

  return {
    status: 'success',
    items: items,
    summary: {
      count: items.length,
      totalGoal: totalGoal,
      totalPledged: totalPledged,
      blessed: blessed
    }
  };
}

// ---- POST: pledge or rsvp ---------------------------------------------------
function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    if (data.type === 'pledge') return handlePledge_(data);
    if (data.type === 'rsvp')   return handleRsvp_(data);
    return json_({ status: 'error', message: 'unknown type' });
  } catch (err) {
    return json_({ status: 'error', message: String(err) });
  }
}

function handlePledge_(d) {
  if (!d.item || !d.amount) return json_({ status:'error', message:'missing fields' });
  var p = tab_(PLEDGES_TAB);
  if (p.getLastRow() === 0) {
    p.appendRow(['Timestamp','Item','Giver Name','Amount','Bank Ref','Confirmed']);
  }
  p.appendRow([
    new Date(),
    String(d.item),
    String(d.name || 'Anonymous'),
    Number(d.amount) || 0,
    String(d.ref || ''),
    'Pending'   // becomes public only when you set this to "Yes"
  ]);
  // Pledge is recorded privately. The public bar does NOT change until the
  // couple confirms the payment, so unverified pledges can't mislead guests.
  return json_({ status:'success', pending:true });
}

function handleRsvp_(d) {
  var r = tab_(RSVP_TAB);
  if (r.getLastRow() === 0) {
    r.appendRow(['Timestamp','Full Name','Email','Phone','Guests','Events','Dietary','Message']);
  }
  // duplicate email guard
  if (d.email) {
    var vals = r.getRange(2,3,Math.max(r.getLastRow()-1,1),1).getValues();
    for (var i=0;i<vals.length;i++){
      if (String(vals[i][0]).toLowerCase() === String(d.email).toLowerCase())
        return json_({ status:'duplicate' });
    }
  }
  r.appendRow([
    new Date(), String(d.name||''), String(d.email||''), String(d.phone||''),
    String(d.guests||''), String(d.events||''), String(d.diet||''), String(d.message||'')
  ]);
  return json_({ status:'success' });
}
