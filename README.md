# Vulnerable Bank : OWASP Top 10 (2017) Project

This is a deliberately vulnerable **local educational Django application** for cyber security base project I. It contains exactly the five selected OWASP 2017 categories:

1. **A1 Injection - SQL Injection**
2. **A2 Broken Authentication**
3. **A5 Broken Access Control / IDOR**
4. **A6 Security Misconfiguration - Django DEBUG**
5. **A7 Cross-Site Scripting (XSS)**

The vulnerable code is active. The corresponding fixes are included immediately next to the flaws as **commented-out code**, so the repository can contain both the flaw and its fix in one version.


## Installation and running

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py initdemo
py manage.py runserver
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py initdemo
python3 manage.py runserver
```

Open `http://127.0.0.1:8000/`.

Demo credentials created by `initdemo`:

- alice / redqueen
- bob / squarepants
- patrick / asteroid

The Broken Authentication flaw deliberately makes the password irrelevant until you apply its fix.

### 5 Flaws from OWASP (2017)

### FLAW 1 - A1 SQL Injection

1. Log in as `bob` (using the real password `squarepants` so this demo does not depend on flaw 2).
2. Open **Note search**.
3. Search for a normal title such as `shopping` and observe Bob's own note. Searching for `salary` should return no result because it belongs to Alice.
4. Search with this payload:

```text
x' OR 1=1 -- 
```

5. The query is supposed to restrict results to Bob, but the vulnerable backend concatenates the title into SQL. The injected `OR 1=1` bypasses that condition, so notes belonging to Alice, Bob and Patrick are returned.
6. In `bank/views.py`, comment out the vulnerable `cursor.execute(sql)` path and uncomment the parameterized-query fix.
7. Restart the server and repeat the same payload. It is treated as plain data and should return no injected rows.

### FLAW 2 - A2 Broken Authentication

1. Log out.
2. Open **Login**.
3. Enter username `alice` and any wrong password such as `wrong-password`.
4. The vulnerable code logs in as Alice because it checks only whether the username exists.
5. In `bank/views.py`, comment out the vulnerable username-only login block and uncomment the `authenticate(...)` fix.
6. Restart the server. The same wrong password is now rejected; `redqueen` works.

### FLAW 3 - A5 Broken Access Control / IDOR

1. Log in as Bob.
2. Open Bob's normal account page: `/account/bob/`.
3. Change only the URL to `/account/alice/`.
4. The vulnerable backend returns Alice's balance even though Bob is authenticated as a different user.
5. In `bank/views.py`, comment out the vulnerable account lookup and uncomment the lookup that also requires `owner=request.user`.
6. Restart the server. Bob can still open `/account/bob/`, but `/account/alice/` returns 404.

### FLAW 4 - A6 Security Misconfiguration / Django DEBUG

1. Open `/crash/`.
2. Because `DEBUG = True`, Django returns its detailed technical exception page.
3. In `vulnsite/settings.py`, change the active setting to `DEBUG = False` using the commented fix already provided.
4. Restart the server and open `/crash/` again. Django returns a generic server-error response instead of the technical debug page.

### FLAW 5 - A7 Stored XSS

1. Log in and open **Comments**.
2. Post this comment:

```html
<script>alert('Stored XSS')</script>
```

3. The comment is stored in the database. The vulnerable backend calls `mark_safe()` on it before rendering, so the browser executes the script whenever the comments page is loaded.
4. In `bank/views.py`, comment out the `mark_safe(comment.text)` line and uncomment `display_text = comment.text`.
5. Restart and reload the page. Django template auto-escaping now displays the script text instead of executing it.

## Screenshot names

See `screenshots`folder.

## Report

See the report on mooc website.
