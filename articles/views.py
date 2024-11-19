from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Article, Comment
from .forms import ArticleForm, CommentForm
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_POST

def articles_main(request):
    keys_to_clear = [key for key in request.session.keys() if key.startswith('viewed_article_')]
    for key in keys_to_clear:
        del request.session[key]
    articles = Article.objects.all().order_by('-created_at')
    context = {
        'articles' : articles,
    }
    return render(request, 'articles/articles_main.html', context)

@login_required
def create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('articles:articles_main')
    else:
        form = ArticleForm()
    context ={
        'form' : form,
    }
    return render(request, 'articles/create.html', context)


def articles_detail(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
   # 세션을 사용하여 조회수 증가 방지
    session_key = f'viewed_article_{article_pk}'
    if session_key not in request.session:
        article.views += 1  # 조회수 증가
        article.save()
        request.session[session_key] = True  # 세션 키 저장
    if request.method == "POST":
       # 댓글 또는 대댓글 작성 처리
       data = json.loads(request.body)
       
       # 댓글 내용과 부모 댓글 ID 가져오기
       content = data.get("content")
       parent_comment_id = data.get("parent_comment_id")

       # 일반 댓글 작성
       if parent_comment_id is None:
           comment = Comment.objects.create(article=article, author=request.user, content=content)
           
           return JsonResponse({
               "success": True,
               "comment_id": comment.id,
               "author": comment.author.username,
               "content": comment.content,
               "created_at": comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
           })

       # 대댓글 작성 처리
       parent_comment = get_object_or_404(Comment, id=parent_comment_id)
       reply_comment = Comment.objects.create(article=article, author=request.user, content=content, parent_comment=parent_comment)
       
       return JsonResponse({
           "success": True,
           "comment_id": reply_comment.id,
           "author": reply_comment.author.username,
           "content": reply_comment.content,
           "created_at": reply_comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
       })

    comments = Comment.objects.filter(article=article, parent_comment=None)
   
    context = {
       "article": article,
       "comments": comments,
   }
    return render(request, "articles/detail.html", context)

@login_required
def toggle_like(request):
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        article = get_object_or_404(Article, id=article_id)

        if article.likes.filter(id=request.user.id).exists():
            article.likes.remove(request.user)  # 좋아요 취소
            liked = False
        else:
            article.likes.add(request.user)  # 좋아요 추가
            liked = True
        
        return JsonResponse({
            'liked': liked,
            'total_likes': article.likes.count(),
        })

@login_required
def articles_delete(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    if article.author != request.user:
        return JsonResponse({'error': '권한이 없습니다.'}, status=403)  # 권한이 없음을 알리는 응답

    article.delete()  # 게시글 삭제
    return JsonResponse({'success': True})

@login_required
def articles_update(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            return redirect('articles:articles_detail', article.pk)
    else:
        form = ArticleForm(instance=article)
    context = {
        'article': article,
        'form': form,
    }
    return render(request, 'articles/update.html', context)

@login_required
def comment_delete(request, comment_id):
   if request.method == "POST":
       comment = get_object_or_404(Comment, id=comment_id)
       if comment.author == request.user:
           comment.delete()
           return JsonResponse({"success": True})
   return JsonResponse({"success": False, "error": "권한이 없습니다."})

@login_required
def toggle_like(request):
   if request.method == "POST":
       article_id = request.POST.get("article_id")
       article = get_object_or_404(Article, id=article_id)

       if article.likes.filter(id=request.user.id).exists():
           article.likes.remove(request.user)  # 좋아요 취소
           liked = False
       else:
           article.likes.add(request.user)  # 좋아요 추가
           liked = True

       return JsonResponse({
           "liked": liked,
           "total_likes": article.likes.count(),
       })
    
@login_required
def toggle_dislike(request):
   if request.method == "POST":
       article_id = request.POST.get("article_id")
       article = get_object_or_404(Article, id=article_id)

       if article.dislikes.filter(id=request.user.id).exists():
           article.dislikes.remove(request.user)  # 싫어요 취소
           disliked = False
       else:
           article.dislikes.add(request.user)  # 싫어요 추가
           disliked = True

       return JsonResponse({
           "disliked": disliked,
           "total_dislikes": article.dislikes.count(),
       })