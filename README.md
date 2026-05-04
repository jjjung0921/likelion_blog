# 개인 기술 블로그 클론 코딩 — 강사용 정답

> 학생 배포용(`student_starter`)의 완성본입니다.
> 1주차 + 2주차 모두 구현되어 있어요.

## 🚀 실행 방법

```bash
python3 -m venv venv
source venv/bin/activate     # Windows: source venv/Scripts/activate
pip install 'django>=5.0,<6.0'
python manage.py runserver
```

브라우저에서 `http://localhost:8000/` 접속.

> `db.sqlite3`가 이미 시드된 상태로 동봉되어 있어요. 별도 migrate 불필요.
> 데이터를 초기화하려면: `rm db.sqlite3 && python manage.py migrate && python manage.py seed_demo`

---

## 📋 구현 사항

### 1주차 (js-object 학습 후)
- ✅ 6개 페이지 HTML/CSS 완성 (Home, Tech 목록, Tech 상세, Projects, About, Daily 목록)
- ✅ Template 상속 (base + _navbar + _footer)
- ✅ NavBar 활성 메뉴 강조
- ✅ 카테고리 칩 active 토글
- ✅ 카테고리 칩 클릭 시 클라이언트 필터링 (`data-category` + `style.display`)

### 2주차 (js-2 학습 후)
- ✅ 페이지 로드 시 `GET /api/posts/<slug>/comments/` → 댓글 목록 렌더링
- ✅ 입력값에 따라 등록 버튼 활성/비활성 (`disabled` 속성)
- ✅ 등록 시 `POST /api/posts/<slug>/comments/` (JSON body) → 응답 댓글 화면 추가
- ✅ 댓글 수 자동 갱신
- ✅ Share `copy ⎘` 버튼 (URL 클립보드 복사)

---

## 🗄️ 데이터 모델

`blog/models.py`에 정의된 모델 (총 9개):

| 모델 | 주요 필드 | 관계 |
|---|---|---|
| **Tag** | slug, label | M:N ← TechPost |
| **Category** | slug, label, order | 1:N → TechPost |
| **TechPost** | slug, title, subtitle, body, read_minutes, views, license, published_at, edited_at | N:1 → Category, M:N → Tag |
| **Comment** | author_name, body, created_at | N:1 → TechPost |
| **DailyCategory** | slug, label, order | 1:N → DailyEntry |
| **DailyEntry** | slug, title, title_en, excerpt, published_at | N:1 → DailyCategory |
| **Project** | slug, name, blurb, year, status, tags, external_url, order | — |
| **Profile** | display_name, headline, role_line, bio_ko, bio_en | 1:N → SkillGroup, Education |
| **SkillGroup** | profile, label, skills | N:1 → Profile |
| **Education** | profile, period, title, subtitle | N:1 → Profile |

> 의도적 단순화: `Comment`는 `User`와 연결하지 않고 `author_name` 문자열만 받아요.
> 학생들이 인증을 안 배웠기 때문에 누구나 임의 이름으로 댓글 가능합니다.
> 인증을 학습하는 다음 단계에서 `User`로 마이그레이션하면 됩니다.

---

## 🔌 백엔드 API

```
GET  /api/posts/<slug>/comments/   →  { comments: [...], count: N }
POST /api/posts/<slug>/comments/   ←  { name, body }  →  { comment: {...}, count: N }
```

- DB(`Comment` 모델)에 영구 저장 — 서버 재시작해도 유지
- `@csrf_exempt` 처리 — 학습 단순화 목적
- 운영 환경에서는 인증 + CSRF 토큰 사용 필요

---

## 📂 학생용과의 차이

| 파일 | 학생용 | 강사용 |
|---|---|---|
| `templates/blog/*.html` | 골격 + TODO 주석 | 완성된 마크업 |
| `static/js/site.js` | TODO 주석 (1주차/2주차 분리) | 완성된 JS |
| `static/css/components.css` | 동일 (완성본 제공) | 동일 |
| `blog/models.py`, `views.py`, `urls.py`, `admin.py`, settings | 동일 | 동일 |
| `db.sqlite3` | 시드된 상태로 동봉 | 시드된 상태로 동봉 |

> 양쪽의 백엔드 코드(models, views, urls, settings)는 완전히 동일합니다.
> 학생들이 손대는 부분은 **HTML 템플릿과 JS** 뿐이에요.

---

## 🎯 채점 포인트 제안

### 1주차
| 항목 | 배점 예시 |
|---|---|
| 6개 페이지가 시안과 일치 | 50% |
| Template 상속/include 구조 | 15% |
| NavBar 활성 메뉴 강조 | 10% |
| 카테고리 칩 active 토글 | 10% |
| 카테고리 클라이언트 필터링 | 15% |

### 2주차
| 항목 | 배점 예시 |
|---|---|
| GET fetch — 댓글 목록 받아 렌더링 | 30% |
| 입력값에 따른 버튼 활성/비활성 | 15% |
| POST fetch — 댓글 등록 + 화면 갱신 | 35% |
| JSON 처리 (`stringify`/`parse`) 정확성 | 10% |
| 에러 처리 (`.catch` 또는 `try-catch`) | 10% |

---

## 🛠️ Admin 패널

`/admin/` 경로로 접속, `admin / admin1234`로 로그인.

수정 가능한 것:
- TechPost (제목, 본문, 카테고리, 태그 등)
- Comment (검토/삭제)
- DailyEntry, Project
- Profile + SkillGroup + Education (inline 편집)

---

## 🔧 커스터마이징

학생들에게 더 도전적인 과제를 내려면:

- **Home 풀 디자인 구현**: 현재는 Hero + 둘러보기 + 최신 노트 3개 섹션만. Figma에는 6개 섹션이 있어요 (시리즈 진행 / Now widget / 코드 스니펫 / Newsletter)
- **`components.css`도 일부 비우기**: `.tech-detail__main`, `.profile-hero` 같은 페이지 레이아웃 클래스는 학생이 작성하게
- **검색 기능 추가**: 검색창의 `input` 이벤트 + 제목/태그 검색 (DB 쿼리 또는 클라이언트 필터)
- **댓글 삭제 기능**: `DELETE /api/posts/<slug>/comments/<id>/` 추가하고 학생이 fetch DELETE로 호출

---

## 💡 학습 흐름과 코드의 매핑

| 학습 자료 | 사용된 부분 |
|---|---|
| Django 기초 (Template 상속, `{% extends %}`, `{% include %}`, `{% for %}`, `{% url %}`) | `base.html`, `_navbar.html`, 모든 페이지 템플릿 |
| JS 심화1 (DOM API, `querySelectorAll`, JS 객체) | 카테고리 칩 토글 + 필터링 (1주차) |
| JS 심화2 (`addEventListener`, input 데이터, JSON, fetch) | 댓글 GET/POST (2주차) |

---

## 🚧 알려진 제약 / 의도적 단순화

- **CSRF 면제**: 댓글 API는 `@csrf_exempt`. 운영에서는 토큰 처리 필수
- **인증 없음**: 누구나 임의 이름으로 댓글 작성 가능. 인증은 다음 학습 단원
- **Home 단순화**: Figma 풀 디자인의 6개 섹션 중 3개만 (Hero / 둘러보기 / 최신 노트)
- **검색 기능 미구현**: searchbar는 UI만 있음
