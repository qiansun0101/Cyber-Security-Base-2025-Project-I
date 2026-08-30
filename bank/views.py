from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe

from .models import Account, Comment


def home(request):
    return render(request, 'bank/home.html')


def insecure_login(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        # flaw 2: A2 broken authentication
        # the backend looks up the username but completely ignores the supplied
        # password. any password therefore authenticates as an existing user.
        user = User.objects.filter(username=username).first()
        if user is not None:
            login(request, user)
            return redirect('home')
        error = 'Invalid username or password.'

        # fix flaw 2: authenticate both username and password.
        # user = authenticate(request, username=username, password=password)
        # if user is not None:
        #     login(request, user)
        #     return redirect('home')
        # error = 'Invalid username or password.'

    return render(request, 'bank/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def note_search(request):
    q = request.GET.get('q', '')
    results = []

    if q:
        # flaw 1: A1 (sql)injection 
        # user input is concatenated directly into an sql statement.
        sql = (
            "SELECT bank_note.id, auth_user.username, bank_note.title, bank_note.body "
            "FROM bank_note JOIN auth_user ON bank_note.owner_id = auth_user.id "
            f"WHERE auth_user.username = '{request.user.username}' "
            f"AND bank_note.title = '{q}'"
        )
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()

            # fix flaw 1: use a parameterized query instead.
            # cursor.execute(
            #     "SELECT bank_note.id, auth_user.username, bank_note.title, bank_note.body "
            #     "FROM bank_note JOIN auth_user ON bank_note.owner_id = auth_user.id "
            #     "WHERE auth_user.username = %s AND bank_note.title = %s",
            #     [request.user.username, q],
            # )
            # rows = cursor.fetchall()

        results = [
            {'id': row[0], 'owner': row[1], 'title': row[2], 'body': row[3]}
            for row in rows
        ]

    return render(request, 'bank/search.html', {'q': q, 'results': results})


@login_required
def account_detail(request, username):
    # flaw 3: A5 Broken Access Control
    # authentication is required, but the backend trusts the object identifier
    # in the URL and does not verify that the requested account belongs to the
    # currently logged-in user.
    account = get_object_or_404(Account, owner__username=username)

    # fix flaw 3: bind the account lookup to the current authenticated user.
    # account = get_object_or_404(Account, owner=request.user, owner__username=username)

    return render(request, 'bank/account.html', {'account': account})


@login_required
def comments(request):
    if request.method == 'POST':
        text = request.POST.get('text', '')
        Comment.objects.create(author=request.user, text=text)
        return redirect('comments')

    comments_from_db = Comment.objects.select_related('author').order_by('-created_at')
    display_comments = []
    for comment in comments_from_db:
        # flaw 5: A7 Cross-Site Scripting (Stored XSS)
        # mark_safe tells Django that attacker-controlled text is trusted HTML,
        # so a stored <script> element is rendered and executed in the browser.
        display_text = mark_safe(comment.text)

        # fix flaw 5: do not mark user input as safe. Django templates will
        # escape the string by default, so script tags are displayed as text.
        # display_text = comment.text

        display_comments.append(
            {
                'author': comment.author.username,
                'text': display_text,
                'created_at': comment.created_at,
            }
        )

    return render(request, 'bank/comments.html', {'comments': display_comments})


def crash(request):
    # this route is only to demonstrate the effect of DEBUG=True.
    raise RuntimeError('Intentional demo exception for the A6 screenshot')
