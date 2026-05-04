# 개인 기술 블로그 클론 코딩

## 🚀 실행 방법

처음 클론한 경우 `db.sqlite3`가 없으므로 아래 순서대로 진행하세요.

```bash
# 1. 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate     # Windows: source venv/Scripts/activate

# 2. Django 설치
pip install 'django>=5.0,<6.0'

# 3. DB 생성 + 테이블 스키마 적용
python manage.py migrate

# 4. 데모 데이터 시딩 (TechPost, Project, Profile 등 샘플 데이터 삽입)
python manage.py seed_demo

# 5. admin 계정 생성 — /admin/ 접속용
python manage.py createsuperuser

# 6. 개발 서버 실행
python manage.py runserver
```

브라우저에서 `http://localhost:8000/` 접속.

> **데이터를 초기화하려면**: `rm db.sqlite3 && python manage.py migrate && python manage.py seed_demo`
>
> **참고**: `db.sqlite3`는 `.gitignore`로 제외되어 있어 각자 로컬에서 생성합니다. `migrations/` 폴더는 git에 포함되어 있어서 `migrate`가 동일한 스키마를 재현합니다.

---

## 🗄️ 데이터 모델

`blog/models.py`에 정의된 모델 (총 9개):

| 모델              | 주요 필드                                                                          | 관계                        |
| ----------------- | ---------------------------------------------------------------------------------- | --------------------------- |
| **Tag**           | slug, label                                                                        | M:N ← TechPost              |
| **Category**      | slug, label, order                                                                 | 1:N → TechPost              |
| **TechPost**      | slug, title, subtitle, body, read_minutes, views, license, published_at, edited_at | N:1 → Category, M:N → Tag   |
| **Comment**       | author_name, body, created_at                                                      | N:1 → TechPost              |
| **DailyCategory** | slug, label, order                                                                 | 1:N → DailyEntry            |
| **DailyEntry**    | slug, title, title_en, excerpt, published_at                                       | N:1 → DailyCategory         |
| **Project**       | slug, name, blurb, year, status, tags, external_url, order                         | —                           |
| **Profile**       | display_name, headline, role_line, bio_ko, bio_en                                  | 1:N → SkillGroup, Education |
| **SkillGroup**    | profile, label, skills                                                             | N:1 → Profile               |
| **Education**     | profile, period, title, subtitle                                                   | N:1 → Profile               |

> `Comment`는 `User`와 연결하지 않고 `author_name` 문자열만 받습니다.

---

## 🛠️ Admin 패널

`/admin/` 경로로 접속, `admin / admin1234`로 로그인.

수정 가능한 것:

- TechPost (제목, 본문, 카테고리, 태그 등)
- Comment (검토/삭제)
- DailyEntry, Project
- Profile + SkillGroup + Education (inline 편집)
