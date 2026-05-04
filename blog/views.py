"""
blog/views.py

각 페이지에 보여줄 데이터를 DB에서 조회해서 template으로 넘겨주는 역할이에요.
2주차에는 댓글을 fetch + JSON API로 다루기 위해 JsonResponse 엔드포인트도 두었어요.

학생 여러분은 이 파일을 수정할 일이 거의 없어요. 데이터 접근 방식만 참고하세요.
"""
import json

from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import (
    Category, Comment, DailyCategory, DailyEntry, Profile, Project, TechPost,
)


# ===== Home 화면용 정적 데이터 (디자인에 박혀있는 카피) =====
HOME_HERO = {
    'eyebrow_left': 'welcome · 환영합니다',
    'eyebrow_right': '— 2026, week 18',
    'h1_line1': '기록하는 일이',
    'h1_line2': '성장이 되는 곳',
    'bio_line1': '아기사자(BL)가 매일 조금씩 적어가는 노트입니다.',
    'bio_line2': '기술, 프로젝트, 그리고 평범한 하루의 단상까지 — 천천히 쌓아 둡니다.',
    'now_writing': '디자인 토큰 시리즈 6편',
}

HOME_AREAS = [
    {'order': '01', 'name': 'About',    'subtitle': '/ profile',
     'desc': '아기사자가 누구인지, 어떤 도구를 쓰고, 어떤 글을 쓰는지에 대한 짧은 소개.',
     'badge': None, 'url_name': 'profile'},
    {'order': '02', 'name': 'Tech',     'subtitle': '/ tech-notes',
     'desc': '코드와 도구에 대한 메모. 디자인 시스템, 타입스크립트, 프론트엔드 잡학.',
     'badge': None, 'url_name': 'tech_list'},  # badge는 view에서 채움
    {'order': '03', 'name': 'Projects', 'subtitle': '/ shipped & wip',
     'desc': '만든 것, 만들고 있는 것. 작은 CLI부터 장난감 같은 사이드 프로젝트까지.',
     'badge': None, 'url_name': 'projects_list'},
    {'order': '04', 'name': 'Daily',    'subtitle': '/ journal',
     'desc': '오늘의 단상과 작은 발견. 커피, 책, 산책, 음악, 그리고 실패한 김밥.',
     'badge': None, 'url_name': 'daily_list'},
]


# ===== 페이지 뷰 =====

def home(request):
    """홈 (Home · landing)"""
    posts_qs = TechPost.objects.select_related('category').prefetch_related('tags')
    latest = list(posts_qs.order_by('-published_at')[:5])
    featured = latest[0] if latest else None
    others = latest[1:] if len(latest) > 1 else []

    latest_dailies = list(
        DailyEntry.objects.select_related('category').order_by('-published_at')[:3]
    )

    # area badge에 통계 채우기 (사본 만들어 사용)
    areas = []
    post_count = TechPost.objects.count()
    project_count = Project.objects.count()
    for a in HOME_AREAS:
        a2 = dict(a)
        if a2['name'] == 'Tech':
            a2['badge'] = f'{post_count} posts'
        elif a2['name'] == 'Projects':
            a2['badge'] = f'{project_count} things'
        areas.append(a2)

    return render(request, 'blog/home.html', {
        'active_nav': 'home',
        'page_number': '00 / 07',
        'hero': HOME_HERO,
        'areas': areas,
        'featured': featured,
        'others': others,
        'latest_dailies': latest_dailies,
    })


def tech_list(request):
    """기술 글 목록 페이지 (TechA)"""
    posts = list(
        TechPost.objects.select_related('category').prefetch_related('tags')
        .order_by('-published_at')
    )
    categories = list(Category.objects.all())
    return render(request, 'blog/tech_list.html', {
        'active_nav': 'tech',
        'page_eyebrow': 'TECH NOTES',
        'page_h1': '만들면서 배운 것들.',
        'page_number': '03 / 05',
        'posts': posts,
        'categories': categories,
    })


def tech_detail(request, slug):
    """기술 글 상세 페이지 (TechC)"""
    post = get_object_or_404(
        TechPost.objects.select_related('category').prefetch_related('tags'),
        slug=slug,
    )
    sections = _parse_body(post.body)
    return render(request, 'blog/tech_detail.html', {
        'active_nav': 'tech',
        'page_number': '03 / 05',
        'post': post,
        'sections': sections,
    })


def _parse_body(body: str):
    """본문 문자열을 섹션 리스트로 변환.
    문법:
      ## 제목  → h2 (id 자동 생성)
      ```      → 코드블록 시작/끝
      그 외     → 단락 (빈 줄로 구분)
    """
    sections = []
    lines = body.splitlines()
    buf = []
    in_code = False
    code_buf = []
    h2_count = 0

    def flush_para():
        nonlocal buf
        text = '\n'.join(buf).strip()
        if text:
            sections.append({'kind': 'p', 'text': text})
        buf = []

    for line in lines:
        if line.strip().startswith('```'):
            if in_code:
                sections.append({'kind': 'code', 'text': '\n'.join(code_buf)})
                code_buf = []
                in_code = False
            else:
                flush_para()
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue
        if line.startswith('## '):
            flush_para()
            h2_count += 1
            sections.append({
                'kind': 'h2',
                'text': line[3:].strip(),
                'anchor': f'sec-{h2_count}',
            })
            continue
        if line.strip() == '':
            flush_para()
            continue
        buf.append(line)

    flush_para()
    if in_code and code_buf:
        sections.append({'kind': 'code', 'text': '\n'.join(code_buf)})
    return sections


def profile(request):
    """About 페이지 (ProfileA)"""
    profile_obj = (
        Profile.objects.prefetch_related('skill_groups', 'education').first()
    )
    return render(request, 'blog/profile.html', {
        'active_nav': 'about',
        'page_number': '02 / 05',
        'profile': profile_obj,
    })



def projects_list(request):
    """프로젝트 목록 페이지 (ProjectsA)"""
    selected_status = request.GET.get('status', 'all').strip().lower()
    qs = Project.objects.all()
    if selected_status in {'live', 'wip', 'archive'}:
        qs = qs.filter(status=selected_status)
    projects = list(qs)
    total_count = Project.objects.count()
    return render(request, 'blog/projects_list.html', {
        'active_nav': 'projects',
        'page_eyebrow': f'PROJECTS · {total_count}',
        'page_h1': '만든 것들.',
        'page_subtitle': 'Things I shipped, and a couple I keep coming back to.',
        'page_number': '04 / 05',
        'projects': projects,
        'selected_status': selected_status,
    })


def daily_list(request):
    """일일 노트 목록 (DailyA)"""
    entries = list(
        DailyEntry.objects.select_related('category').order_by('-published_at')
    )
    categories = list(DailyCategory.objects.all())
    return render(request, 'blog/daily_list.html', {
        'active_nav': 'daily',
        'page_eyebrow': 'DAILY NOTES',
        'page_h1': '오늘의 한 페이지.',
        'page_number': '05 / 05',
        'entries': entries,
        'categories': categories,
    })


# ===== 댓글 JSON API (2주차 — fetch + JSON으로 호출) =====

@csrf_exempt  # 학습용으로 CSRF 면제. 운영 환경에서는 토큰 처리 필요.
@require_http_methods(['GET', 'POST'])
def comments_api(request, slug):
    """
    GET  /api/posts/<slug>/comments/  → 해당 글의 댓글 목록 JSON
    POST /api/posts/<slug>/comments/  → JSON body {name, body} 받아 댓글 추가, 새 댓글 반환
    """
    try:
        post = TechPost.objects.get(slug=slug)
    except TechPost.DoesNotExist:
        return JsonResponse({'error': 'post not found'}, status=404)

    if request.method == 'GET':
        comments = list(post.comments.all().order_by('created_at'))
        return JsonResponse({
            'comments': [
                {
                    'name': c.author_name,
                    'body': c.body,
                    'date': c.date_display,
                }
                for c in comments
            ],
            'count': len(comments),
        })

    # POST
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)

    name = (payload.get('name') or '').strip()
    body = (payload.get('body') or '').strip()
    if not name or not body:
        return JsonResponse({'error': 'name and body are required'}, status=400)

    comment = Comment.objects.create(
        post=post,
        author_name=name[:40],
        body=body[:500],
    )
    return JsonResponse({
        'comment': {
            'name': comment.author_name,
            'body': comment.body,
            'date': comment.date_display,
        },
        'count': post.comments.count(),
    }, status=201)
