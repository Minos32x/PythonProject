from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth.models import User
from .forms import  RegUserForm
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from .models import *

import re
from django.db.models import Q

def all_users(request):
    all_usr = User.objects.all()
    return render(request, "adminPanel/all_users.html", {"all_usrs": all_usr})


def home(request):
    context={'allCategories':Categories.objects.all(),'allPosts':Posts.objects.all().order_by('-post_date')[:5]}
    return render(request,"adminPanel/home.html",context)


def admin(request):
    return render(request, "adminPanel/Dashboard.html")

def block(request, usr_id):
    us = User.objects.get(id=usr_id)
    us.is_active = 0
    us.save()
    all_usr = User.objects.all()
    return render(request, "adminPanel/all_users.html", {"all_usrs": all_usr})


def unblock(request, usr_id):
    us = User.objects.get(id=usr_id)
    us.is_active = 1
    us.save()
    all_usr = User.objects.all()
    return render(request, "adminPanel/all_users.html", {"all_usrs": all_usr})


def update(request, usr_id):
    usr = User.objects.get(id=usr_id)
    usr_form = RegUserForm(instance=usr)
    if request.method == "POST":
        usr_form = RegUserForm(request.POST, instance=usr)
        if usr_form.is_valid():
            usr_form.save()
            return HttpResponseRedirect("/blogersite/allusers/")

    return render(request, "adminPanel/new.html", {"form": usr_form})


def delete(request, usr_id):
    us = User.objects.get(id=usr_id)
    us.delete()

    all_usr = User.objects.all()
    return render(request, "adminPanel/all_users.html", {"all_usrs": all_usr})


def promote(request, usr_id):
    us = User.objects.get(id=usr_id)
    us.is_superuser = 1
    us.save()
    all_usr = User.objects.all()
    return render(request, "adminPanel/all_users.html", {"all_usrs": all_usr})


def addnew(request):
    usr_form = RegUserForm()
    if request.method == "POST":
        usr_form = RegUserForm(request.POST)
        if usr_form.is_valid():
            usr_form.save()
            return HttpResponseRedirect("/blogersite/allusers/")
    return render(request, "adminPanel/new.html", {"form": usr_form})


def register(request):
    usr_form=RegUserForm()

    if request.method=="POST":
        usr_form=RegUserForm(request.POST)
        if usr_form.is_valid():
            usermail = User.objects.filter(email=request.POST['email'])
            if usermail.exists():
                return render(request, "adminPanel/register.html", {"form": usr_form, "repeatedmail": 1})
            usr_form.save()
            reg_username = request.POST['username']
            reg_password = request.POST['password1']
            user = authenticate(username=reg_username, password=reg_password)
            login(request, user)
            return HttpResponseRedirect("/blogersite/home")
    return render(request, "adminPanel/register.html",{"form":usr_form})


@login_required
def logout(request):
    django_logout(request)
    logout(request)
    return HttpResponseRedirect("/blogersite/home")


def login_form(request):
    if request.method == 'POST':

        name = request.POST['username']
        password = request.POST['password']

        # authenticate first search for the user in database and if found
        # it returns user object
        # and if it didn't find a user it will return None
        user = authenticate(username=name, password=password)
        if user:
            if user.is_active == 0:
                return render(request, 'adminPanel/login_form.html',{"block":1})



        if user is not None:  # this means we found the user in database
            login(request, user)  # this means we put the user id in the session


            return HttpResponseRedirect("/blogersite/home")
        else:

            return render(request,"adminPanel/login_form.html",{"openreg":1})
    return render(request, 'adminPanel/login_form.html')


# this is a decorator
# https://docs.djangoproject.com/en/2.0/topics/auth/default/#the-login-required-decorator
@login_required
def logged_in_only(request):
    return HttpResponse('you are authenticated')


def managerPanel(request):
    return render(request, "adminPanel/Dashboard.html")


def allCategories(request):
    all_categories = Categories.objects.all()
    context = {"allCategories": all_categories}
    return render(request, "adminPanel/all_cat.html", context)


def getCategory(request,cat_id):
    get_category = Categories.objects.get(id=cat_id)
    context = {"allCategories": get_category}
    return render(request, "adminPanel/cat_details.html", context)


def newCategory(request):
    category_form = CategoryForm()
    if request.method == "POST":
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            return HttpResponseRedirect('/blogersite/allCategories/')
    context = {"form": category_form}
    return render(request, 'adminPanel/new_cat.html', context)


def category_delete(request, cat_id):
    obj = Categories.objects.get(id=cat_id)
    obj.delete()
    return HttpResponseRedirect('/blogersite/allCategories/')


def category_edit(request, cat_id):
    category = Categories.objects.get(id=cat_id)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect('/blogersite/allCategories/')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'adminPanel/edit_cat.html', {'form': form})


#######################################
# ForbideentWords

def allForbidden(request):
    all_forbidden = ForbiddenWords.objects.all()
    context = {"allForbidden": all_forbidden}
    return render(request, "adminPanel/all_forbid.html", context)


# def getForbidden(request, forbid_id):
#     get_category = Categories.objects.get(id=forbid_id)
#     context = {"allCategories": get_category}
#     return render(request, "adminPanel/cat_details.html", context)


def newForbidden(request):
    forbidden_form = ForbiddenForm()
    if request.method == "POST":
        forbidden_form = ForbiddenForm(request.POST)
        if forbidden_form.is_valid():
            forbidden_form.save()
            return HttpResponseRedirect('/blogersite/allForbidden/')
    context = {"form": forbidden_form}
    return render(request, 'adminPanel/new_forbid.html', context)


def forbidden_delete(request, forbidden_id):
    obj = ForbiddenWords.objects.get(id=forbidden_id)
    obj.delete()
    return HttpResponseRedirect('/blogersite/allForbidden/')


def forbidden_edit(request, forbidden_id):
    forbid = ForbiddenWords.objects.get(id=forbidden_id)

    if request.method == "POST":
        form = ForbiddenForm(request.POST, instance=forbid)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect('/blogersite/allForbidden/')
    else:
        form = ForbiddenForm(instance=forbid)
    return render(request, 'adminPanel/edit_forbid.html', {'form': form})


####################################################
# Tag Names
####################################################
def allTags(request):
    all_tag = TagNames.objects.all()
    context = {"allTags": all_tag}
    return render(request, "adminPanel/all_tag.html", context)


def newTag(request):
    tag_form = TagForm()
    if request.method == "POST":
        tag_form = TagForm(request.POST)
        if tag_form.is_valid():
            tag_form.save()
            return HttpResponseRedirect('/blogersite/allTags/')
    context = {"form": tag_form}
    return render(request, 'adminPanel/new_tag.html', context)


def tag_delete(request, tag_id):
    obj = TagNames.objects.get(id=tag_id)
    obj.delete()
    return HttpResponseRedirect('/blogersite/allTags/')


def tag_edit(request, tag_id):
    tag = TagNames.objects.get(id=tag_id)

    if request.method == "POST":
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect('/blogersite/allTags/')
    else:
        form = TagForm(instance=tag)
    return render(request, 'adminPanel/edit_tag.html', {'form': form})


####################################################
# Posts
####################################################

def allPosts(request):
    all_posts = Posts.objects.all()
    context = {"allPosts": all_posts}
    return render(request, "adminPanel/all_post.html", context)


def getPosts(request, post_id):
    get_posts = Posts.objects.get(id=post_id)
    context = {"allPosts": get_posts}
    return render(request, "adminPanel/post_details.html", context)


def newPost(request):
    post_form = PostForm()
    if request.method == "POST":
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            # post_form.post_image = request.FILES['post_image']
            post_form.save()
            return HttpResponseRedirect('/blogersite/allPosts/')
    context = {"form": post_form}
    return render(request, 'adminPanel/new_post.html', context)


def post_delete(request, post_id):
    obj = Posts.objects.get(id=post_id)
    obj.delete()
    return HttpResponseRedirect('/blogersite/allPosts/')


def post_edit(request, post_id):
    post = Posts.objects.get(id=post_id)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect('/blogersite/allPosts/')
    else:
        form = PostForm(instance=post)
    return render(request, 'adminPanel/edit_post.html', {'form': form})


def search(request):
    #found_entries = Posts.objects.filter(post_title__icontains=request.GET['query']).order_by('-post_date')
    #context = {"allPosts": found_entries}
    #return render(request, "adminPanel/home.html", context)

    posts = Posts.objects.filter(post_title__icontains=request.GET['query'])
    try:
        tag=TagNames.objects.get(tag_name__icontains=request.GET['query'])
        posts2=Posts.objects.filter(post_tags=tag.id)
    except:
        return render(request, "adminPanel/home.html",{'allPosts':posts})
    else:
        return render(request, "adminPanel/home.html",{'allPosts':posts2})


def getCategoryPosts(request, cat_id):
    get_category = Categories.objects.get(id=cat_id)
    context = {'allPosts':Posts.objects.filter(	post_cat_id=get_category.id).order_by('-post_date')}
    return render(request, "adminPanel/home.html", context)

##################################################################
#comments & reply
#################################################################


# def getThePost(request, post_id):
#     get_posts = Posts.objects.get(id=post_id)
#     context = {"allPosts": get_posts}
#     return render(request, "adminPanel/post.html", context)
#
#
# def addComment(request, post_id):
#     print post_id, request.user
#     if request.method == 'POST':
#         comment = CommentForm(request.POST, request.FILES)
#         if comment.is_valid():
#             comment = comment.save(commit=False)
#             # return an object that hasn't yet been saved to the database to do proccessing on it
#         # comment.comment_body = wordsCleaner(comment.comment_body)
#         comment.post = Posts.objects.get(id=post_id)
#         # comment.User = User.objects.get(id = request.user.id)
#         comment.comment_user_id_id = request.user.id
#         comment.comment_post_id_id = post_id
#
#         comment.save()
#         return redirect(request.path)
#     return HttpResponseRedirect("/main/" + post_id + "/post")
#
#
# def addReply(request, post_id, commentID):
#     if request.method == 'POST':
#         reply = CommentForm(request.POST, request.FILES)
#         if reply.is_valid():
#             reply = reply.save(commit=False)
#         # reply.comment_body = wordsCleaner(reply.comment_body)
#         reply.post = Posts.objects.get(id=post_id)
#         # comment.User = User.objects.get(id = request.user.id)
#         reply.comment_user_id_id = request.user.id
#         reply.comment_post_id_id = post_id
#         reply.reply_comment_id = Comment.objects.get(id=commentID)
#
#         reply.save()
#         return redirect(request.path)
#     return HttpResponseRedirect("/main/" + post_id + "/post")

def postPage(request, post_id):
    get_posts = Posts.objects.get(id=post_id)
    context = {"allPosts": get_posts}
    return render(request, "adminPanel/post.html", context)

# def postPage(request,post_id):
# 	post=Posts.objects.get(id =post_id)
# 	comment=Comment.objects.filter(id= post_id)
# 	reply=Reply.objects.filter(id= post_id)
# 	context={'postshow':post , 'comment' : comment, 'reply' : reply}
# 	return render(request, 'adminPanel/post.html' ,context)


# def addComment(request, post_id):
#     comment_post_id = Posts.objects.get(id = post_id)
#     user_id = request.user.id
#     if request.method == "POST":
#         comment = CommentForm(request.POST)
#         if comment.is_valid():
#             comment = comment.save(commit=False)
#             # return an object that hasn't yet been saved to the database to do processing on it
#             comment.id = comment_post_id
#             comment.id = user_id
#             comment.checkForbidden()
#             comment.save()
#             return redirect('/blogersite/'+post_id+'/post')
#     else:
#         form = CommentForm()
#         context = {"form": form}
#     return render(request, 'adminPanel/add_comments.html', context)


def addComment(request, post_id):
    comment_post_id = Posts.objects.get(id = post_id)
    user_id = request.user.id
    if request.method == "POST":
        comment = CommentForm(request.POST)
        if comment.is_valid():
            comment = comment.save(commit=False)
            # return an object that hasn't yet been saved to the database to do processing on it
            comment.id = comment_post_id
            comment.id = user_id
            comment.checkForbidden()
            comment.save()
            return redirect('/blogersite/'+post_id+'/post')
    else:
        form = CommentForm()
        context = {"form": form}
    return render(request, 'adminPanel/add_comments.html', context)




def addReply(request, post_id, comment_id):
    user_id = request.user.id
    if request.method == "POST":
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.comment_post_id = post_id
            reply.reply_comment_id = int(comment_id)
            reply.comment_user_id = int(user_id)
            reply.checkForbidden()
            reply.save()
            return redirect('/blogersite/post/'+post_id+'/show')
    else:
        form = ReplyForm()
    return render(request, 'blogersite/reply_comment.html', {'form': form})

