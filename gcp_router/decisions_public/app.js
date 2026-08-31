// Décisions — front de la webapp.
// Le login/mot de passe partent à Odoo ; les fiches reviennent filtrées par
// la règle user_id d'Odoo. La zone de saisie n'apparaît QUE quand une
// réponse est utile (rejet = commentaire obligatoire).
(function () {
  const $ = (sel) => document.querySelector(sel);

  let session = null;   // { uid, cookie }
  let filter = 'attente';
  let all = [];

  // ------------------------------------------------------------------ state
  function store() {
    try { localStorage.setItem('tds', JSON.stringify(session)); } catch (_) {}
  }
  function loadStore() {
    try { return JSON.parse(localStorage.getItem('tds') || 'null'); } catch (_) { return null; }
  }

  function showLogin() { $('#login').classList.remove('hidden'); $('#app').classList.add('hidden'); }
  function showApp() { $('#login').classList.add('hidden'); $('#app').classList.remove('hidden'); }

  // ------------------------------------------------------------------ api
  // Via Caddy, la webapp vit sous /decisions/ (handle_path enlève le préfixe
  // avant le proxy). En local, elle est à la racine. Le front ajoute le
  // préfixe selon l'URL qu'il voit.
  function apiBase() {
    return location.pathname.indexOf('/decisions') === 0 ? '/decisions' : '';
  }
  async function api(path, body) {
    const res = await fetch(apiBase() + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body || {}),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Erreur inconnue.');
    return data;
  }

  // ------------------------------------------------------------------ render
  const PRIO = { '1': ['P1', 'priorite-1'], '2': ['P2', 'priorite-2'], '3': ['P3', 'priorite-3'] };
  const ETAT_LBL = { attente: 'À décider', approuve: 'Approuvée', rejete: 'Rejetée' };

  function stripHtml(s) {
    const div = document.createElement('div');
    div.innerHTML = s || '';
    return div.textContent || div.innerText || '';
  }
  function condense(s, n) {
    const t = stripHtml(s).replace(/\s+/g, ' ').trim();
    return t.length > n ? t.slice(0, n) + '…' : t;
  }

  function render() {
    const visibles = all.filter((d) => d.etat === filter);
    $('#c-attente').textContent = all.filter((d) => d.etat === 'attente').length;
    $('#c-approuve').textContent = all.filter((d) => d.etat === 'approuve').length;
    $('#c-rejete').textContent = all.filter((d) => d.etat === 'rejete').length;

    if (filter === 'attente') {
      $('#headline').textContent = 'Ce qu'on te demande';
      $('#subtitle').textContent = 'Ce qui attend ta réponse.';
    } else if (filter === 'approuve') {
      $('#headline').textContent = 'Déjà approuvé';
      $('#subtitle').textContent = 'Tes décisions qui ont donné le feu vert.';
    } else {
      $('#headline').textContent = 'Rejeté';
      $('#subtitle').textContent = 'Ce que tu as refusé, avec ton commentaire.';
    }

    $('#empty').classList.toggle('hidden', visibles.length > 0);
    const list = $('#list');
    list.innerHTML = '';

    visibles.forEach((d) => {
      const p = PRIO[d.priorite] || PRIO['3'];
      const card = document.createElement('article');
      card.className = 'card';

      const head = document.createElement('div');
      head.className = 'card-head';
      head.innerHTML = `
        <span class="prio ${p[1]}">${p[0]}</span>
        <h2 class="card-title"></h2>
      `;
      head.querySelector('.card-title').textContent = d.name || '(sans titre)';

      const origin = d.origine ? `<span class="origin">de ${escapeHtml(d.origine)}</span>` : '';
      const resume = d.resume ? `<p class="resume">${escapeHtml(condense(d.resume, 220))}</p>` : '';
      const date = new Date(d.create_date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });

      card.innerHTML += `
        <div class="card-meta">${origin}<span class="date">${date}</span></div>
        ${resume}
      `;

      // actions
      const actions = document.createElement('div');
      actions.className = 'actions';

      if (d.etat === 'attente') {
        const bOpen = document.createElement('button');
        bOpen.className = 'btn';
        bOpen.textContent = 'Lire le détail';
        bOpen.onclick = () => toggleDetail(d);
        actions.appendChild(bOpen);
      } else {
        const comment = d.commentaire
          ? `<div class="comment"><span class="lbl">Ta note :</span>${escapeHtml(condense(d.commentaire, 180))}</div>`
          : '';
        if (comment) actions.insertAdjacentHTML('beforebegin', comment);
        const b = document.createElement('button');
        b.className = 'btn ghost';
        b.textContent = 'Lire le détail';
        b.onclick = () => toggleDetail(d);
        actions.appendChild(b);
      }
      card.appendChild(actions);

      // detail (repliable)
      const detail = document.createElement('div');
      detail.className = 'detail hidden';
      detail.innerHTML = `
        <div class="detail-body"></div>
        <div class="detail-actions">
          <textarea class="saisie hidden" placeholder="Ta réponse ou le motif de ton refus…"></textarea>
          <div class="detail-btns hidden">
            <button class="btn danger" data-a="rejeter">Rejeter</button>
            <button class="btn primary" data-a="approuver">Approuver</button>
          </div>
          <p class="error hidden"></p>
        </div>
      `;
      const db = detail.querySelector('.detail-body');
      db.innerHTML = `
        <h3>Contexte complet</h3>
        ${d.resume ? `<div class="ctx">${d.resume}</div>` : '<p class="sub">Pas de contexte.</p>'}
        ${d.commentaire ? `<div class="ctx note">${escapeHtml(d.commentaire)}</div>` : ''}
      `;

      const txt = detail.querySelector('.saisie');
      const btns = detail.querySelector('.detail-btns');
      detail.querySelectorAll('.detail-btns .btn').forEach((b) => {
        b.onclick = async () => {
          const err = detail.querySelector('.error');
          err.classList.add('hidden');
          b.disabled = true;
          try {
            await api(`/api/decisions/${d.id}/action`, {
              action: b.dataset.a, commentaire: txt.value.trim(), session,
            });
            await refresh();
          } catch (e) {
            err.textContent = e.message;
            err.classList.remove('hidden');
            b.disabled = false;
          }
        };
      });

      card.appendChild(detail);
      list.appendChild(card);
    });
  }

  function toggleDetail(d) {
    const cards = document.querySelectorAll('.card');
    cards.forEach((c) => {
      const det = c.querySelector('.detail');
      if (det && c.contains(detailOf(d))) return;
    });
    // retrouver la carte contenant cette décision
    [...document.querySelectorAll('.card')].forEach((card) => {
      const det = card.querySelector('.detail');
      const isTarget = card.querySelector('.card-title') &&
        card.dataset.id === String(d.id);
      if (isTarget) {
        det.classList.toggle('hidden');
        const txt = det.querySelector('.saisie');
        const btns = det.querySelector('.detail-btns');
        // La saisie ne se dégrise que si on va REJETER (commentaire obligatoire).
        // Pour approuver, on la garde visible mais facultative.
        btns.classList.remove('hidden');
        txt.classList.remove('hidden');
      } else {
        det.classList.add('hidden');
      }
    });
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function detailOf() { return null; }

  // ------------------------------------------------------------------ data
  async function refresh() {
    const data = await api('/api/decisions', { session });
    all = data.filter((d) => d && d.id);
    all.forEach((d) => { d.id = Number(d.id); });
    render();
  }

  // ------------------------------------------------------------------ login
  async function doLogin(email, password) {
    const data = await api('/api/login', { login: email, password });
    session = { uid: data.uid, cookie: data.cookie };
    store();
    $('#user-name').textContent = email;
    showApp();
    await refresh();
  }

  // ------------------------------------------------------------------ init
  document.addEventListener('DOMContentLoaded', () => {
    const saved = loadStore();
    if (saved && saved.uid) {
      session = saved;
      $('#user-name').textContent = saved.login || 'Connecté';
      showApp();
      refresh().catch(() => { session = null; showLogin(); });
    } else {
      showLogin();
    }

    $('#login-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const err = $('#login-error');
      err.classList.add('hidden');
      const btn = $('#login-form button');
      btn.disabled = true;
      try {
        await doLogin($('#login-email').value, $('#login-pass').value);
      } catch (ex) {
        err.textContent = ex.message;
        err.classList.remove('hidden');
        btn.disabled = false;
      }
    });

    $('#logout').addEventListener('click', () => {
      session = null;
      localStorage.removeItem('tds');
      $('#login-pass').value = '';
      showLogin();
    });

    $('#filters').addEventListener('click', (e) => {
      const chip = e.target.closest('.chip');
      if (!chip) return;
      document.querySelectorAll('.chip').forEach((c) => c.classList.remove('active'));
      chip.classList.add('active');
      filter = chip.dataset.f;
      render();
    });
  });
})();
