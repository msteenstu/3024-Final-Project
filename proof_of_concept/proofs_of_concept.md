# Proof-of-Concept Demonstrations

The following proof-of-concept demonstrations illustrate how each code snippet introduces vulnerabilities into the codebase and detail the step-by-step exploitation process for each vulnerability. The exploit demonstrations were performed with the Flask application deployed locally. ****Do not**** attempt any of these exploits on real web applications; these demonstrations are meant to emphasize the dangers of insecure coding practices rather than to target a real platform.

# SQL Injection

## Overview and Vulnerable Code

The bookstore application contains a SQL injection vulnerability in the book genre search functionality. This security flaw exists because user-supplied input is directly embedded in the SQL query without parameterization or input validation, allowing the input to be treated as SQL code instead of data. The primary weakness of this implementation is that untrusted input is concatenated in the `text()` function instead of being used in a parameterized query. Additionally, the user-supplied input is not validated against an allow-list of acceptable book genres nor is it sanitized of common SQL syntax, increasing the risk of SQL code being executed (MITRE, n.d.). These factors combined create a SQL injection vulnerability that can be exploited for unauthorized data retrieval. However, because the ORM executes only one SQL statement per `execute()` call, stacked queries are not supported, which limits the likelihood of unauthorized data modification. As demonstrated in the proof-of-concept, this vulnerability is primarily exploited through UNION-based SQL injection attacks to extract data from the database.

#### The Vulnerable Code Snippet

The code snippet included below highlights the vulnerable query function located in the [shop_operations.py](../src/app/shop_operations.py#L27-L43) file.

```
def query_books_by_genre(user_input):
    if user_input.lower() == 'all':
        return query_all_books()
    else:
        return db.session.execute(
            text(f"SELECT * FROM books WHERE genre = '{user_input.lower()}'")
            ).fetchall()
```

## Exploitation Walkthrough

### Preconditions and Required Materials

* The Flask application running locally
* A browser
* At least one user account exists in the database (two accounts existed during this demonstration)
* The user is authenticated within the application
* Documentation or knowledge of SQLite functions
* Documentation on [the schema table in SQLite](https://www.sqlite.org/schematab.html)

### Step 1 - Prove Injection Is Possible and Discover the Database Type

To establish that the application is vulnerable to SQL injection, it had to be verified that input unrelated to valid book genres could influence the behavior of the query. A UNION-based attack payload was constructed to determine whether arbitrary values could be injected into the query's output and to identify the number of columns returned. By aligning the payload columns with the number of columns displayed in the book listings table, it was determined that the query returned seven columns, confirming that SQL injection was possible. An example test payload is included below.

```
'UNION SELECT NULL, NULL, NULL, NULL, NULL, NULL, NULL--
```

Once the structure of the payload was established, the database type needed to be identified so database-specific syntax and table structures could be used for subsequent attacks. By replacing one column value with version functions from common RDBMS platforms, it was discovered that the application uses a SQLite database, as the `sqlite_version()` function executed successfully. The query used to further verify the UNION-based payload structure and identify the database type is included below with an image of its output.

```
'UNION SELECT NULL, sqlite_version(), NULL, NULL, NULL, NULL, NULL--
```

![img](screenshots/sqli_database_version.png "Identify the Database Type")

### Step 2 - Perform Database Reconnaissance on the Schema Table

With the database type discovered, database reconnaissance was performed to gather more information about the tables within the database. To accomplish this, the database's schema table (`sqlite_master`) was queried. According to SQLite's (n.d.) documentation, this table contains details about the database's objects, including their names and types. The UNION-based injection payload used to retrieve the types and names of database objects from the `sqlite_master` table is included below, along with its output demonstrating that the table names were successfully enumerated.

```
'UNION SELECT NULL, type, tbl_name, NULL, NULL, NULL, NULL FROM sqlite_master--
```

![img](screenshots/sqli_database_recon.png "Gathering Information from the Schema Table")

### Step 3 - Identify the Structure of the `users` Table

The previous exploitation step revealed there was a `users` table containing customer data. To discover what sensitive information from the `users` table could be targeted, the structure of the table needed to be determined. Using information about the schema table from SQLite's (n.d.) documentation, an injection payload was crafted to retrieve the structure of the table and its column names from `sqlite_master` . The following payload and output screenshot demonstrate that the structure of the `users` table could be successfully obtained, providing insight into which columns could be targeted in future SQL injection attacks.

```
'UNION SELECT NULL, sql, NULL, NULL, NULL, NULL, NULL FROM sqlite_master WHERE tbl_name= 'users'--
```

![img](screenshots/sqli_user_table_structure.png "Results from Querying the Structure of the users Table")

### Step 4 - Access Customer Data from the `users` Table

With the structure of the `users` table retrieved, sensitive customer data could be queried and extracted for subsequent exploitation. The columns identified as likely to contain sensitive customer information were *id*, *email*, *name*, *salt*, and *password*. The following attack payload used these fields in the order they appeared in the database to improve output readability, with the payload results shown below.

```
'UNION SELECT NULL, id, email, name, salt, password, NULL FROM users--
```

![img](screenshots/sqli_user_information.png "Database Leak of User Information")

The successful database enumeration and exposure of customer data emphasize the severity of the SQL injection vulnerability within the book genre search functionality, as sensitive user information can be easily exfiltrated without proper authorization.

### Risk Analysis

The SQL injection vulnerability present in the book genre query introduces a significant security risk that compromises Book Worm's confidentiality. Exploitation of this vulnerability could result in the exposure of the entire database schema, enabling further database reconnaissance and providing attackers with insight into the application's structural design. Alongside schema disclosure, sensitive user information may also be extracted, leading to unauthorized account access and the improper disclosure of user information. This type of vulnerability is particularly damaging in an e-commerce application as the exposure of customer and account data poses significant privacy risks.

### General Remediation Advice

This vulnerability can be mitigated by parameterizing all SQL queries through SQLAlchemy's ORM querying methods instead of concatenating user input for queries using the text() function. Additionally, all input can be compared against an allow-list to validate user-supplied input before it is processed.

# Weak Cryptographic Practices

## Overview and Vulnerable Code

The application implements weak cryptographic practices for password storage by hashing user passwords with the deprecated MD5 algorithm and a static, reused salt. Although the application enforces a basic password policy, complexity requirements alone do not guarantee password protection when combined with insecure hashing techniques. The use of MD5 is strongly discouraged because it is a deprecated, fast hashing algorithm that is susceptible to brute-force attacks (OWASP, 2025). While storing the salt "books" in the database is not considered poor security practice, using a short, shared salt significantly reduces its effectiveness (Defuse Security, n.d.). If the database is exposed, threat actors can obtain the password hashes and the shared salt to recover user passwords using automated cracking tools and brute-force attack techniques as seen in the following demonstration.

#### The Vulnerable Code Snippet

The weak hashing method mentioned below is located in the [user_operations.py](../src/app/user_operations.py#L36-L54) module.

```
def hash_user_password(password):
    hash_salt = 'books'

    # Inspired by guidance from The Python Wiki (n.d.) on using the MD5 hashing function.
    hashed_password = hashlib.md5(
        hash_salt.encode('utf-8') + password.encode('utf-8')
    ).digest()
    return hash_salt, hashed_password
```

## Exploitation Walkthrough

### Preconditions and Required Materials

* The Flask application running locally
* At least one user account exists in the database (two accounts existed during this demonstration)
* At least one recovered password binary (two were used for this demonstration which were discovered in the previous SQL injection exploit walkthrough)
* Terminal access
* Python3 installed in the local environment
* Hashcat
* The [rockyou.txt](https://weakpass.com/wordlists/rockyou.txt) word list
* Stroz Friedberg's (2024) [password complexity rule list](https://github.com/strozfriedberg/sf-password-research/blob/main/rules/8-complex-1k.rule)

### Step 1 - Format Obtained Passwords for Hashcat

The password hashes and salt were obtained from the `users` table via a SQL injection attack shown in a previous demonstration. However, this data had to be formatted before Hashcat could be used. Since Hashcat expects hashes to be in a hexadecimal format, the raw password bytes were converted to hexadecimal using Python's `hex()` method in the terminal.

```
python3 -c 'print((b"+A\x0bA\x16\x94\x03\xaa\xadc\x0b\xa2\xd0BY\x9b").hex())'
2b410b41169403aaad630ba2d042599b

python3 -c 'print((b"m\xfa^\x84\xf4\xd1\x89$!\x1e\x93\x99\xcf\xd0\xb3C").hex())'
6dfa5e84f4d18924211e9399cfd0b343
```

After converting the password hashes to hexadecimal, they were stored in a text file with the retrieved salt appended to each hash using Hashcat's expected `hash:salt` format. This format allows Hashcat to parse the hash and salt as different components. The text file, `password_hashes.txt`, was created to store each hash and the salt on separate lines so Hashcat would process them individually.

```
2b410b41169403aaad630ba2d042599b:books
6dfa5e84f4d18924211e9399cfd0b343:books
```

### Step 2 - Identify the Hashing Algorithm Used

Since the application's source code was not leaked, the hashing algorithm applied to the user passwords was initially unknown. To identify the hashing algorithm, Hashcat's `--identify` command was used to analyze the extracted password hashes. With the formatted `password_hashes.txt` file, the following command was executed:

```
hashcat --identify password_hashes.txt
```

![img](screenshots/hashcat_identifies_hashes.png "Identify the Password Hash with Hashcat")

The command returned several possible algorithms that could have been used to hash the passwords. Based on this output, combined with the hashes' consistent length and hexadecimal format characteristic of MD5, it was determined that the passwords were most likely hashed using the MD5 algorithm (The PHP Documentation Group, n.d.).

### Step 3 - Run Hashcat Against the Prepared Hashes

With the hashes and salt formatted in the `password_hashes.txt` file and several potential hash modes for MD5 identified, Hashcat was used to crack the password hashes using a dictionary attack approach. By testing different algorithm modes, it was discovered that mode 20, which corresponds to the MD5 algorithm with the salt prepended before the password, produced successful results. The command used to crack the password hashes can be broken down as follows:

* `-m 20` selects the hashing mode which corresponds to the MD5 algorithm with the salt prepended to the password.
* `-a 0` specifies the attack mode as a dictionary attack.
* `password_hashes.txt` contains the extracted password hashes with their salt values.
* `rockyou.txt` is composed of commonly used passwords.
* `-r 8-complex-1k.rule` applies rule-based transformations to generate password variations that reflect common password patterns aligned with typical password complexity requirements.

The fully constructed Hashcat command used to crack the user password hashes was:

```
hashcat -m 20 -a 0 password_hashes.txt rockyou.txt -r 8-complex-1k.rule
```

![img](screenshots/hashcat_cracks_passwords_highlighted.png "Hashcat Cracks User Passwords")

The command's output highlights that the two passwords recovered from the database, Blue@ocean#12 and HelloWorld1!, were successfully cracked. The successful recovery of the passwords highlights Book Worm's weak cryptographic practices regarding password storage.

### Risk Analysis

Weak password hashing creates an authentication risk that negatively impacts Book Worm's confidentiality and integrity. If attackers gain access to the database and obtain password hashes and the static salt, they can efficiently recover user passwords using common, readily available hash-cracking tools. Within the bookstore application, exploitation of this vulnerability can result in stolen user credentials, unauthorized access to user accounts, exposure of order information, and unauthorized account activities such as placing fraudulent orders or deleting a user's account. In a customer-facing application, weak cryptographic practices for user credentials greatly increase the risk of user exploitation and reputational damage due to the exposure of customer information.

### General Remediation Advice

The risks from weak hashing methods can be avoided by hashing user passwords with modern algorithms such as Argon2 or ChaCha20, each with a unique salt.

# Insecure Direct Object Reference (IDOR)

## Overview and Vulnerable Code

Book Worm contains an access control flaw with the invoice viewing functionality, specifically an insecure direct object reference (IDOR) vulnerability. This vulnerability is a form of access control failure because the application exposes references to database objects through modifiable identifiers without enforcing authorization checks on the user requesting the object (OWASP, 2024). With the invoice retrieval functionality, users can directly access invoice objects by modifying the order number in the URL. This user-supplied number is the only filter used in the invoice retrieval query; there are no filters applied using the authenticated user's ID. As a result, ownership of the invoice is not enforced during retrieval, and the requesting user is given access to the object without validating that the user is permitted to access it. The following proof-of-concept demonstrates how a user can enumerate order invoices in the system without being associated with them.

#### The Vulnerable Code Snippets

The following code snippets from the [routes.py](../src/app/routes.py#L256-L273) file and the invoice query function located in the [shop_operations.py](../src/app/shop_operations.py#L188-L199) file are both related to the IDOR vulnerability.

```
From routes.py
@app.route('/user/orders/<int:invoice_id>', methods=['GET'])
@login_required
def view_order(invoice_id):
  
    invoice = get_buyer_invoice(invoice_id)
    invoice_checkout_items = invoice.cart.checkout_items
  
    return render_template('view_order.html', invoice = invoice, checkout_items = invoice_checkout_items)
```

```
From shop_operations.py
def get_buyer_invoice(invoice_id: int):  
    return Invoice.query.filter_by(id = invoice_id).first()
```

## Exploitation Walkthrough

### Preconditions and Required Materials

* The Flask application running locally
* A browser
* At least two user accounts exist in the database
* The user is authenticated within the application
* At least one order has been placed in the application by the unauthenticated user

### Step 1 - Identifying the Current Authenticated User's Orders

Upon viewing the orders page as an authenticated user, it was observed that the current user had placed one order. Accessing the order using the "View Order Invoice" button directed the user to a page containing details about the invoice. On this webpage, the URL includes the order number, indicating that it is used as an identifier to retrieve order invoices. The expected order viewing functionality as an authenticated user is shown in the screenshots below.

![img](screenshots/idor_current_authenticated_user_view.png "The Current Authenticated User's Order View")

![img](screenshots/idor_current_authenticated_user_order.png "Current Authenticated User's Order")

### Step 2 - Viewing Other User Orders

Since the currently authenticated user only has one order with the invoice number 2, it can be inferred that there are other orders in the system with similar numeric identifiers, such as 1. Since it was determined that the application would retrieve an order invoice using the order number in the URL, the order number was updated from 2 to 1. The system retrieved another user's order and displayed it on the webpage, as seen below.

```
https://127.0.0.1:5000/user/orders/1
```

![img](screenshots/idor_other_user_order.png "Viewing Another User's Order")

The successful retrieval of an order that was not placed by the currently authenticated user verifies the presence of a broken access control flaw within the order invoice viewing functionality.

### Risk Analysis

The IDOR proof-of-concept illustrates the impact of this vulnerability on Book Worm's confidentiality. To exploit this vulnerability, a threat actor only needs to be authenticated on the system and discover the URL used to access individual order invoices. In Book Worm, this vulnerability could expose sensitive user information, including order payment details, user names, and addresses, resulting in significant privacy risks. This type of vulnerability can be very concerning in e-commerce platforms, where users expect their order details and personal information to remain private and securely stored within the system.

### General Remediation Advice

Mitigation of the IDOR vulnerability would involve obtaining the user's ID in the `view_order` route and using it as a filter in the invoice query. This would prevent unauthorized access to the invoice object because the system would verify that the user is associated with it prior to the object being returned.

# Cross-Site Request Forgery (CSRF)

## Overview and Vulnerable Code

The Book Worm application contains several programming inconsistencies and misconfigurations that coalesce into a cross-site request forgery (CSRF) vulnerability. A CSRF vulnerability occurs when attackers can perform unintended, state-changing actions on behalf of an authenticated user by exploiting request verification mechanisms that rely on session cookies instead of tokens (PortSwigger, n.d.). With the bookstore implementation, automatic CSRF protection was disabled to support the custom CSRF validation function, and the application is configured to accept session cookies from cross-site requests. Additionally, the CSRF validation function that verifies tokens prior to processing form data was not consistently applied to all routes, specifically the `delete_account` route. Also, the delete account form does not include a CSRF token, so request verification relies solely on session cookies. As a result, forged requests originating from another source can be processed as legitimate user requests, enabling unauthorized account deletion, as demonstrated in the upcoming proof-of-concept.

#### The Vulnerable Code Snippets and Configuration Settings

The following configurations in the [init.py](../src/app/__init__.py#L32-43) file highlight the necessary settings required to enable CSRF exploitation.

```
Configuration settings informed by Boucher (2022).
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'

# Custom CSRF protection implementation adapted from Flask-WTF's (n.d.) documentation.
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()
app.config["WTF_CSRF_CHECK_DEFAULT"] = False
csrf.init_app(app)
```

These code snippets show the inconsistent CSRF protections applied in the application, including the lack of a CSRF token on the account deletion form from the [user_account.html](../templates/user_account.html#L9-L17) file and that the `delete_account` endpoint being excluded in the CSRF protection list in the [routes.py](../src/app/routes.py#L19-L34) file.

```
From user_account.html
<form method="post" action="{{ url_for('delete_account') }}">
   <!--The absense of a validation token makes this form vulnerable to a Cross-Site Request Forgery attack.-->
   <label>Name</label>
   <input type="text" name="name" value="{{user.name}}" disabled>
   <label>Email</label>
   <input type="text" name="email" value="{{user.email}}" disabled>
   <button type="submit">Delete Account</button>
</form>
```

```
From routes.py
# Custom CSRF protection implementation adapted from Flask-WTF's (n.d.) documentation.
@app.before_request
def validate_csrf_manually():
    if request.endpoint in [
        'login', 'signup', 'logout', 'view_books', 'add_book_to_cart', 'complete_order'] \
        and request.method == 'POST':
            csrf.protect()
```

## Exploitation Walkthrough

### Preconditions and Required Materials

* The Flask application running locally
* A browser
* At least one user account exists in the database
* The user is authenticated within the application
* A Python web server
* An HTML [(such as this one)](csrf_exploit/index.html) containing a form that submits a POST request to the `/user/delete` endpoint

**Note:**

* To simulate a realistic CSRF attack scenario, a malicious webpage was hosted using Python's built-in HTTP server. Even though both the Book Worm application and the malicious webpage were hosted locally for demonstration purposes, they were running on different ports to represent separate applications so a cross-site request could be simulated. In a real-world scenario, the attacker would host this webpage publicly and attempt to trick the victim into visiting it via a malicious link. For this demonstration, the interaction is simulated by manually navigating to the malicious webpage while a user is authenticated in Book Worm.

### Step 1 - Deploy a Python Web Server with a Malicious Webpage

To delete an authenticated user's account without accessing their account, a malicious webpage can be created and hosted using Python's built-in web server. This webpage must contain a form that sends a POST request to the `/user/delete` endpoint. This endpoint can be identified through application testing as an authenticated user or by exploring the application's web structure. When the form on the webpage is submitted, a POST request is sent to the target endpoint as long as Book Worm is actively running. The following Python command and HTML file demonstrate how the exploit is constructed and deployed.

```
Malicious HTML Webpage File
<h3>Oh no, looks like something went wrong trying to access that page on Book Worm!</h3>

<!--Malicious HTML form influenced by Boucher (2022).-->
<form hidden id="delete" action="https://127.0.0.1:5000/user/delete" method="post" novalidate>
</form>

<p>Click the button below to refresh the page and reload Book Worm</p>
<button onClick="deleteUserAccount()">Click to Refresh Page</button>

<script>
    function deleteUserAccount() {
        document.getElementById('delete').submit();
    }
</script>
```

```
Python Command executed to host the malicious webpage: python3 -m http.server
```

### Step 2 - Have the Authenticated User Visit the Malicious Webpage

To execute the CSRF attack, the user must access the malicious webpage while authenticated in Book Worm. This is because the attack requires that the user's session cookies remain active. The image below shows the demonstration user, Ada Lovelace, actively authenticated in the system and viewing their orders.

![img](screenshots/csrf_show_authenticated_user.png "Authenticated User View")

Next, the authenticated user must navigate from Book Worm to the malicious webpage on the Python web server. For this demonstration, the user manually accessed the webpage in a separate browser tab. This webpage was designed to deceive the user into believing that one of Book Worm's pages failed to load and then prompted the user to refresh the page. The user would assume the webpage is legitimate and trust its message because they are an active Book Worm customer. An image of the malicious webpage can be seen below.

![img](screenshots/csrf_malicious_server_deployed.png "Malicious Webpage Open in Browser")

### Step 3 - Sending the Forged Request and Deleting the User's Account

With the authenticated user on the malicious webpage, the "Click to Refresh Page" button was clicked, forging a POST request to the `/user/delete` endpoint. During form submission, the browser included the authenticated user's session cookies with the request, allowing the application to treat the request as legitimate and process it. After the forged request was processed, Ada Lovelace's account was deleted.

The now unauthenticated user was redirected to Book Worm's home page, where a message was displayed indicating the account was deleted. The UI was also updated to reflect the authentication change. The subsequent screenshot shows the user deletion message and the unauthenticated UI view for the test user Ada Lovelace.

![img](screenshots/csrf_user_deleted.png "Webpage Confirming the User was Deleted")

The successful deletion of Ada Lovelace's account demonstrates that the `/user/delete` endpoint is vulnerable to forged requests, as the application fails to properly verify the origin of the account deletion request.

### Risk Analysis

The CSRF vulnerability present in the Book Worm application severely compromises the system's integrity. Although successful exploitation relies on several preliminary steps, including developing a malicious webpage, hosting it, and tricking a user into sending the forged request, the attack can still be executed with minimal technical resources because the application fails to properly validate the origin of the delete account request. Successful exploitation of the CSRF vulnerability results in the unauthorized deletion of user accounts, which harms the reliability and integrity of the order records because the link between the user and their orders is erased. CSRF vulnerabilities similar to this can be particularly damaging in e-commerce platforms because sensitive user information and account details can be altered without the user's knowledge, eroding user trust in the platform and compromising data integrity.

Additionally, an excessive number of forged requests could degrade system performance or potentially trigger a denial-of-service condition. As a result, Book Worm's availability could be negatively impacted by the CSRF vulnerability.

### General Remediation Advice

The CSRF vulnerability in the application can be mitigated by applying CSRF protection to all routes and ensuring every form includes a valid CSRF token. Additionally, converting all HTML forms to Flask-WTF forms would also remediate this vulnerability because Flask-WTF automatically generates and validates CSRF tokens for all POST requests by default.
