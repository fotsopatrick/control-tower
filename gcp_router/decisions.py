"""The decisions desk: a human approves or refuses what an agent proposed.

Ported from the original Node app (tour-decisions) that ran on the second VPS.
Behaviour is unchanged, with two differences:

  * it talks to Odoo over HTTPS instead of plain HTTP, because on Cloud Run the
    request leaves Google's network and a password must not travel in clear;
  * nothing is stored here -- no password, no session. The browser holds the
    Odoo session cookie and sends it back on each call, exactly as before.

Odoo applies its own rule (user_id): a person sees only their own decisions.
And a refusal without a written reason is rejected: a silent "no" teaches
nobody anything.
"""
import json
import os
import re
import urllib.error
import urllib.request

ODOO = os.environ.get("ODOO_URL", "https://tour.matourdecontrole.fr").rstrip("/")
ODOO_DB = os.environ.get("ODOO_DB", "tour_test")
TIMEOUT = 45


def _post(path, payload, cookie=None):
    req = urllib.request.Request(
        ODOO + path, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    if cookie:
        req.add_header("Cookie", cookie)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        raw = r.read().decode("utf-8", "replace")
        set_cookie = r.headers.get_all("Set-Cookie") or []
    try:
        data = json.loads(raw)
    except ValueError:
        raise RuntimeError("Odoo answered something that is not JSON")
    if data.get("error"):
        e = data["error"]
        raise RuntimeError(e.get("message") or e.get("faultString") or "Odoo error")
    return data.get("result"), set_cookie


def authenticate(login, password):
    """Log in with the person's own Odoo credentials. Nothing is kept here."""
    result, set_cookie = _post("/web/session/authenticate",
                               {"jsonrpc": "2.0", "method": "call",
                                "params": {"db": ODOO_DB, "login": login,
                                           "password": password}, "id": 1})
    cookie = ""
    for sc in set_cookie:
        m = re.match(r"session_id=([^;]+)", sc)
        if m:
            cookie = "session_id=" + m.group(1)
            break
    uid = (result or {}).get("uid")
    if not uid:
        raise RuntimeError("Credentials refused by the tower.")
    return uid, cookie


def call_kw(cookie, model, method, args, kwargs=None):
    result, _ = _post("/web/dataset/call_kw",
                      {"jsonrpc": "2.0", "method": "call",
                       "params": {"model": model, "method": method,
                                  "args": args, "kwargs": kwargs or {}},
                       "id": 1}, cookie=cookie)
    return result


FIELDS = ["name", "origine", "resume", "priorite", "etat",
          "create_date", "decide_le", "commentaire"]


def list_decisions(uid, cookie):
    ids = call_kw(cookie, "decision.fiche", "search",
                  [[["user_id", "=", uid],
                    ["etat", "in", ["attente", "approuve", "rejete"]]]],
                  {"order": "etat, priorite, create_date desc", "limit": 200})
    recs = call_kw(cookie, "decision.fiche", "read", [ids, FIELDS])
    return recs if isinstance(recs, list) else []


def decide(uid, cookie, decision_id, action, commentaire):
    """approve or reject one decision. A refusal needs a written reason."""
    commentaire = (commentaire or "").strip()
    if action == "rejeter" and not commentaire:
        raise ValueError("Write a reason first: a silent refusal teaches nobody.")
    if action == "approuver" and commentaire:
        call_kw(cookie, "decision.fiche", "write",
                [[decision_id], {"commentaire": commentaire}])
    method = "action_approuver" if action == "approuver" else "action_rejeter"
    call_kw(cookie, "decision.fiche", method, [[decision_id]])
    return True
