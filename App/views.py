from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponseNotFound
from faunadb import query as q
import pytz
from faunadb.objects import Ref
from faunadb.client import FaunaClient
import hashlib
import datetime

client = FaunaClient(secret="secret_key")

# Create your views here.
def login(request):
    if request.method == "POST":
        username = request.POST.get("username").strip().lower()
        password = request.POST.get("password")

        try:
            user = client.query(q.get(q.match(q.index("user"), username)))
            if hashlib.sha512(password.encode()).hexdigest() == user["data"]["password"]:
                request.session["user"] = {
                    "id": user["ref"].id(),
                    "username": user["data"]["username"]
                }
                return redirect("App:index")
            else:
                raise Exception()
        except:
            messages.add_message(request, messages.INFO,"You have supplied invalid login credentials, please try again!", "danger")
            return redirect("App:login")
    return render(request,"login.html")


def register(request):
    if request.method == "POST":

        username = request.POST.get("username").strip().lower()
        email = request.POST.get("email").strip().lower()
        password = request.POST.get("password")

        try:
            user = client.query(q.get(q.match(q.index("user"), username)))
            messages.add_message(request, messages.INFO, 'User already exists with that username.')
            return redirect("App:register")
        except:
            user = client.query(q.create(q.collection("Users"), {
                "data": {
                    "username": username,
                    "email": email,
                    "password": hashlib.sha512(password.encode()).hexdigest(),
                    "date": datetime.datetime.now(pytz.UTC)
                }
            }))
            messages.add_message(request, messages.INFO, 'Registration successful.')
            return redirect("App:login")
    return render(request,"register.html")


def index(request):
    return render(request,"index.html")

def search_books(request):
    if request.GET.get("search"):
        try:
            search=request.GET.get("search")
            book= client.query(q.get(q.match(q.index("book_index"), search)))["data"]
            context={"book":book}
            return render(request,"search-books.html",context)
        except:
            messages.add_message(request, messages.INFO, 'No book found.')
            return render(request,"search-books.html")
    else:
        try:
            books= client.query(q.paginate(q.match(q.index("book_index_all"), "True")))["data"]
            book_count=len(books)
            page_number = int(request.GET.get('page', 1))
            book = client.query(q.get(q.ref(q.collection("Books"), books[page_number-1].id())))["data"]
            context={"count":book_count,"book":book, "next_page": min(book_count, page_number + 1), "prev_page": max(1, page_number - 1)}
            return render(request,"search-books.html",context)
        except:
            messages.add_message(request, messages.INFO, 'No book found.')
            return render(request,"search-books.html")

def add_book(request):
    if request.method=="POST":
        title= request.POST.get("title")
        genres=request.POST.get("genres")
        summary=request.POST.get("summary")
        pages=request.POST.get("pages")
        copies=request.POST.get("copies")
        author= request.POST.get("author")
        about=request.POST.get("about")
        try:
            book = client.query(q.get(q.match(q.index("book_index"), title)))
            messages.add_message(request, messages.INFO, 'Book Already Exists')
            return redirect("App:add_book")
        except:
            book = client.query(q.create(q.collection("Books"), {
                "data": {
                    "title":title,
                    "genres": genres,
                    "summary": summary,
                    "pages":pages,
                    "copies":copies,
                    "author":author,
                    "about":about,
                    "availability":"True"
                }
            }))
            messages.add_message(request, messages.INFO, 'Book added Successfully')
            return redirect("App:add_book")
    return render(request,"add-book.html")


def detail(request,slug):
    try:
        book= client.query(q.get(q.match(q.index("book_index"), slug)))["data"]
        context={"book":book}
        return render(request,"detail.html",context)
    except:
        return render(request,"detail.html")
