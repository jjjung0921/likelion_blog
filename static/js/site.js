/* =========================================================
   site.js — 정답 완성본
   1주차: 카테고리 칩 active 토글 + 클라이언트 필터링
   2주차: fetch + JSON API로 댓글 가져오기 / 등록
   ========================================================= */

(function () {
  'use strict';

  // ===========================================================
  // 1주차 — 카테고리 칩 토글 + 필터링
  // ===========================================================

  document.querySelectorAll('[data-filter-group]').forEach(function (group) {
    const chips = group.querySelectorAll('.chip');
    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        // 1-A. 모든 chip 초기화 후 클릭한 것만 active
        chips.forEach(function (c) {
          c.classList.remove('chip--accent');
          c.classList.add('chip--outline');
        });
        chip.classList.remove('chip--outline');
        chip.classList.add('chip--accent');

        // 1-B. 필터링: chip.dataset.filter 값에 맞춰 보이기/숨기기
        const filter = chip.dataset.filter;
        const list = document.querySelector('[data-post-list]');
        if (!list) return;
        list.querySelectorAll('[data-category]').forEach(function (item) {
          const show = (filter === 'all') || (item.dataset.category === filter);
          item.style.display = show ? '' : 'none';
        });
      });
    });
  });


  // ===========================================================
  // 2주차 — 댓글: fetch + JSON API
  // ===========================================================

  const form = document.querySelector('[data-comment-form]');
  if (form) {
    initComments(form);
  }

  function initComments(form) {
    const slug = form.dataset.postSlug;
    const apiUrl = '/api/posts/' + slug + '/comments/';

    const author = document.getElementById('comment-author');
    const body = document.getElementById('comment-body');
    const submit = form.querySelector('[data-submit-comment]');
    const listEl = document.getElementById('comment-list');
    const countEl = document.querySelector('[data-comment-count]');

    // 2-A. 페이지 로드 시 GET → 댓글 목록 받아 렌더링
    fetch(apiUrl)
      .then(function (res) { return res.json(); })
      .then(function (data) {
        listEl.innerHTML = '';
        data.comments.forEach(function (c) { listEl.appendChild(buildComment(c)); });
        countEl.textContent = data.count;
      })
      .catch(function (err) {
        console.error('failed to load comments', err);
      });

    // 2-B. 입력값에 따라 등록 버튼 활성/비활성
    function syncButton() {
      const hasAuthor = author.value.trim().length > 0;
      const hasBody = body.value.trim().length > 0;
      submit.disabled = !(hasAuthor && hasBody);
    }
    author.addEventListener('input', syncButton);
    body.addEventListener('input', syncButton);

    // 2-C. 등록 버튼 → POST
    submit.addEventListener('click', function () {
      const payload = {
        name: author.value.trim(),
        body: body.value.trim(),
      };
      if (!payload.name || !payload.body) return;

      submit.disabled = true;
      fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
        .then(function (res) {
          if (!res.ok) throw new Error('server error');
          return res.json();
        })
        .then(function (data) {
          listEl.appendChild(buildComment(data.comment));
          countEl.textContent = data.count;
          author.value = '';
          body.value = '';
          syncButton();
        })
        .catch(function (err) {
          console.error('failed to post comment', err);
          submit.disabled = false;
          alert('댓글 등록에 실패했어요.');
        });
    });
  }

  function buildComment(c) {
    const wrap = document.createElement('div');
    wrap.className = 'comment-item';

    const avatar = document.createElement('span');
    avatar.className = 'avatar avatar--32';
    avatar.textContent = (c.name || '').slice(0, 2).toUpperCase();
    wrap.appendChild(avatar);

    const bodyEl = document.createElement('div');
    bodyEl.className = 'comment-item__body';

    const header = document.createElement('div');
    header.className = 'comment-item__header';
    const nameEl = document.createElement('span');
    nameEl.className = 'comment-item__name';
    nameEl.textContent = c.name;
    const dateEl = document.createElement('span');
    dateEl.className = 'comment-item__date';
    dateEl.textContent = c.date;
    header.appendChild(nameEl);
    header.appendChild(dateEl);
    bodyEl.appendChild(header);

    const content = document.createElement('p');
    content.className = 'comment-item__content';
    content.textContent = c.body;
    bodyEl.appendChild(content);

    wrap.appendChild(bodyEl);
    return wrap;
  }


  // ===========================================================
  // 보너스 — Share copy 버튼
  // ===========================================================
  document.querySelectorAll('[data-share="copy"]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      navigator.clipboard.writeText(location.href).then(function () {
        const original = btn.textContent;
        btn.textContent = 'copied ✓';
        setTimeout(function () { btn.textContent = original; }, 1500);
      }).catch(function () { /* ignore */ });
    });
  });
})();
