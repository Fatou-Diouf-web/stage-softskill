from django.shortcuts import render, get_object_or_404
from .models import BlogPost, BlogCategory, BlogTag


def post_list(request):
    """Liste des articles"""
    posts = BlogPost.objects.filter(status='published').order_by('-published_at')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, slug):
    """Détail d'un article"""
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    return render(request, 'blog/post_detail.html', {'post': post})


def category_detail(request, slug):
    """Détail d'une catégorie"""
    category = get_object_or_404(BlogCategory, slug=slug, is_active=True)
    posts = BlogPost.objects.filter(category=category, status='published')
    return render(request, 'blog/category_detail.html', {'category': category, 'posts': posts})


def tag_detail(request, slug):
    """Détail d'un tag"""
    tag = get_object_or_404(BlogTag, slug=slug)
    posts = tag.posts.filter(status='published')
    return render(request, 'blog/tag_detail.html', {'tag': tag, 'posts': posts})
