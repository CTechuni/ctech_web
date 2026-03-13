// communities-logic.js
// Lógica del panel de comunidades - archivo externo para evitar problemas de compilación

import { AuthManager } from './auth.js';

var allCommunities = [];
var availableLeaders = [];

async function loadCommunities() {
    try {
        var data = await AuthManager.fetch('/communities/');
        allCommunities = Array.isArray(data) ? data : [];
        var el = document.getElementById('communitiesCount');
        if (el) el.textContent = allCommunities.length + ' espacios activos';
        renderTable(allCommunities);
    } catch (e) { console.error(e); }
}

async function loadLeaders() {
    try {
        var users = await AuthManager.fetch('/users/leaders/');
        availableLeaders = Array.isArray(users) ? users.filter(function (u) { return !u.community_id; }) : [];
        populateLeaderSelects();
    } catch (e) { console.error(e); }
}

function populateLeaderSelects() {
    var ids = ['createLeaderSelect', 'editLeaderSelect'];
    ids.forEach(function (id) {
        var sel = document.getElementById(id);
        if (!sel) return;
        var cur = sel.value;
        var lbl = id === 'createLeaderSelect' ? 'Seleccionar líder...' : 'Sin líder';
        sel.innerHTML = '<option value="">' + lbl + '</option>';
        availableLeaders.forEach(function (u) {
            var opt = document.createElement('option');
            opt.value = u.id;
            opt.textContent = u.name_user;
            if (u.id == cur) opt.selected = true;
            sel.appendChild(opt);
        });
    });
}

function renderTable(list) {
    var tbody = document.getElementById('communitiesBody');
    if (!tbody) return;
    if (!list.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading-row">No hay comunidades para mostrar</td></tr>';
        return;
    }
    var html = '';
    list.forEach(function (c) {
        var isActive = (c.status_community || c.status) === 'active';
        var date = c.created_at ? new Date(c.created_at).toLocaleDateString() : '-';
        var logoUrl = c.logo_url || c.logo || '';
        var logoHtml;
        if (logoUrl && logoUrl.length < 10) {
            logoHtml = '<div class="logo-placeholder" style="font-size:1.2rem">' + logoUrl + '</div>';
        } else if (logoUrl) {
            logoHtml = '<img src="' + logoUrl + '" class="community-logo" />';
        } else {
            logoHtml = '<div class="logo-placeholder">' + (c.name_community || '?')[0].toUpperCase() + '</div>';
        }
        var id = c.id_community || c.id;
        html += '<tr>';
        html += '<td>' + logoHtml + '</td>';
        html += '<td><strong>' + (c.name_community || '-') + '</strong></td>';
        html += '<td>' + (c.leader_name || '<span style="color:#94A3B8;font-style:italic">Sin asignar</span>') + '</td>';
        html += '<td><code>' + (c.code || '-') + '</code></td>';
        html += '<td><span class="badge ' + (isActive ? 'badge-success' : 'badge-danger') + '">' + (isActive ? 'Activa' : 'Inactiva') + '</span></td>';
        html += '<td style="color:#64748B;font-size:0.8rem">' + date + '</td>';
        html += '<td><div style="display:flex;gap:0.5rem">';
        html += '<button class="action-icon-btn" onclick="openEditById(' + id + ')" title="Editar">';
        html += '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" /></svg>';
        html += '</button>';
        html += '<button class="action-icon-btn" onclick="deleteCommunity(' + id + ')" title="Eliminar" style="color:#ef4444;border-color:#fee2e2">';
        html += '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" /></svg>';
        html += '</button>';
        html += '</div></td></tr>';
    });
    tbody.innerHTML = html;
}

window.openEditById = function (id) {
    var c = allCommunities.find(function (item) { return (item.id_community || item.id) == id; });
    if (!c) return;
    document.getElementById('editId').value = id;
    document.getElementById('editName').value = c.name_community || '';
    document.getElementById('editCode').value = c.code || '';
    var logoUrl = c.logo_url || '';
    document.getElementById('editLogoUrlInput').value = logoUrl;
    var preview = document.getElementById('editLogoPreview');
    if (preview) {
        if (logoUrl && logoUrl.length < 10) {
            preview.innerHTML = logoUrl;
            document.querySelectorAll('.edit-emoji').forEach(function (b) {
                b.classList.toggle('active', b.dataset.emoji === logoUrl);
            });
        } else if (logoUrl) {
            preview.innerHTML = '<img src="' + logoUrl + '" />';
            document.querySelectorAll('.edit-emoji').forEach(function (b) { b.classList.remove('active'); });
        } else {
            preview.innerHTML = '';
        }
    }
    populateLeaderSelects();
    var sel = document.getElementById('editLeaderSelect');
    if (sel && c.leader_id) sel.value = c.leader_id;
    openModal('editModal');
};

window.deleteCommunity = async function (id) {
    if (!confirm('Eliminar esta comunidad?')) return;
    try {
        await AuthManager.fetch('/communities/' + id, { method: 'DELETE' });
        loadCommunities();
    } catch (e) { alert(e.message); }
};

function openModal(id) { var el = document.getElementById(id); if (el) el.classList.add('open'); }
function closeModal(id) { var el = document.getElementById(id); if (el) el.classList.remove('open'); }

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('searchInput')?.addEventListener('input', function (e) {
        var q = e.target.value.toLowerCase();
        renderTable(allCommunities.filter(function (c) {
            return (c.name_community || '').toLowerCase().includes(q) || (c.code || '').toLowerCase().includes(q);
        }));
    });

    document.getElementById('createBtn')?.addEventListener('click', function () {
        var f = document.getElementById('createForm');
        if (f) f.reset();
        var prev = document.getElementById('logoPreview');
        if (prev) prev.innerHTML = '';
        var inp = document.getElementById('logoUrlInput');
        if (inp) inp.value = '';
        document.querySelectorAll('#createEmojiGrid .emoji-opt').forEach(function (b) { b.classList.remove('active'); });
        openModal('createModal');
    });

    document.querySelectorAll('[data-close]').forEach(function (btn) {
        btn.addEventListener('click', function () { closeModal(btn.getAttribute('data-close')); });
    });

    document.querySelectorAll('.modal-backdrop').forEach(function (m) {
        m.addEventListener('click', function (e) { if (e.target === m) closeModal(m.id); });
    });

    document.querySelectorAll('#createEmojiGrid .emoji-opt').forEach(function (btn) {
        btn.addEventListener('click', function () {
            document.querySelectorAll('#createEmojiGrid .emoji-opt').forEach(function (b) { b.classList.remove('active'); });
            btn.classList.add('active');
            document.getElementById('logoUrlInput').value = btn.getAttribute('data-emoji');
            document.getElementById('logoPreview').innerHTML = btn.getAttribute('data-emoji');
        });
    });

    document.querySelectorAll('#editEmojiGrid .emoji-opt').forEach(function (btn) {
        btn.addEventListener('click', function () {
            document.querySelectorAll('#editEmojiGrid .emoji-opt').forEach(function (b) { b.classList.remove('active'); });
            btn.classList.add('active');
            document.getElementById('editLogoUrlInput').value = btn.getAttribute('data-emoji');
            document.getElementById('editLogoPreview').innerHTML = btn.getAttribute('data-emoji');
        });
    });

    document.getElementById('logoUploadBtn')?.addEventListener('click', function () {
        document.getElementById('logoFileInput').click();
    });

    document.getElementById('editLogoUploadBtn')?.addEventListener('click', function () {
        document.getElementById('editLogoFileInput').click();
    });

    document.getElementById('logoFileInput')?.addEventListener('change', function (e) {
        if (e.target.files[0]) handleFileUpload(e.target.files[0], 'logoPreview', 'logoUrlInput', 'createEmojiGrid');
    });

    document.getElementById('editLogoFileInput')?.addEventListener('change', function (e) {
        if (e.target.files[0]) handleFileUpload(e.target.files[0], 'editLogoPreview', 'editLogoUrlInput', 'editEmojiGrid');
    });

    document.getElementById('createForm')?.addEventListener('submit', async function (e) {
        e.preventDefault();
        var btn = document.getElementById('submitCreateBtn');
        var prev = btn.textContent;
        btn.disabled = true; btn.textContent = 'Creando...';
        try {
            var fd = new FormData(this);
            var body = {
                name_community: fd.get('name'),
                code: fd.get('code'),
                logo_url: document.getElementById('logoUrlInput').value,
                status_community: 'active'
            };
            var leaderId = fd.get('leader_id');
            var endpoint = leaderId ? '/communities/with-leader' : '/communities/';
            var payload = leaderId ? { community: body, leader_id: parseInt(leaderId) } : body;
            await AuthManager.fetch(endpoint, { method: 'POST', body: JSON.stringify(payload) });
            closeModal('createModal');
            loadCommunities();
        } catch (e) { alert(e.message); }
        finally { btn.disabled = false; btn.textContent = prev; }
    });

    document.getElementById('editForm')?.addEventListener('submit', async function (e) {
        e.preventDefault();
        var btn = document.getElementById('submitEditBtn');
        var prev = btn.textContent;
        btn.disabled = true; btn.textContent = 'Guardando...';
        try {
            var fd = new FormData(this);
            var id = fd.get('id');
            var body = {
                name_community: fd.get('name'),
                code: fd.get('code'),
                logo_url: document.getElementById('editLogoUrlInput').value
            };
            await AuthManager.fetch('/communities/' + id, { method: 'PATCH', body: JSON.stringify(body) });
            var leaderId = fd.get('leader_id');
            if (leaderId) await AuthManager.fetch('/communities/' + id + '/assign-user/' + leaderId, { method: 'POST' });
            closeModal('editModal');
            loadCommunities();
        } catch (e) { alert(e.message); }
        finally { btn.disabled = false; btn.textContent = prev; }
    });

    loadCommunities();
    loadLeaders();
});

async function handleFileUpload(file, previewId, inputId, gridId) {
    var preview = document.getElementById(previewId);
    if (preview) preview.innerHTML = 'Subiendo...';
    try {
        var fd = new FormData();
        fd.append('file', file);
        var data = await AuthManager.fetch('/communities/upload', { method: 'POST', body: fd });
        if (data && data.url) {
            document.getElementById(inputId).value = data.url;
            if (preview) preview.innerHTML = '<img src="' + data.url + '" />';
            document.querySelectorAll('#' + gridId + ' .emoji-opt').forEach(function (b) { b.classList.remove('active'); });
        }
    } catch (e) {
        if (preview) preview.innerHTML = '';
        alert('Error al subir la imagen');
    }
}
