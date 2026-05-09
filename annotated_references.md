# References

Boucher, W. (2022, February 23).  *SameSite: HAX – Exploiting CSRF with the default SameSite Policy* . Pulse Security. https://pulsesecurity.co.nz/articles/samesite-lax-csrf

* This proof-of-concept highlighted how the SameSite cookie setting can enable CSRF attacks. Additionally, this resource outlined how a malicious HTML page could be used to execute a CSRF attack.

Defuse Security. (n.d.).  *Secure Salted Password Hashing - how to do it properly* .https://crackstation.net/hashing-security.htm

* Outlined common salt storage practices in the database and insecure hashing methodologies such as using short salts and reusing them.

Dib, F. (n.d.).  *regex101: Credit Card Date (MM/YY)* . Regex101. https://regex101.com/r/AFarfB/1

* This resource was used to help create a regex pattern that validates user-supplied credit card expiration date information from the complete order form.

Flask. (n.d.).  *Message Flashing — Flask Documentation (3.1.x)* . https://flask.palletsprojects.com/en/stable/patterns/flashing/

* Flask's documentation for message flashing was used to craft the structure of the messages delivered to the user.

Flask-WTF. (n.d.). CSRF Protection — Flask-WTF Documentation (0.15.x). https://flask-wtf.readthedocs.io/en/0.15.x/csrf/

* This resource was used to learn how to implement CSRF protection on routes handling POST requests.

MITRE. (n.d.).  *CWE-89: Improper neutralization of special elements used in an SQL command ('SQL injection’) (4.20)* . https://cwe.mitre.org/data/definitions/89.html

* Provided insight for the SQL injection vulnerability overview about how a lack of input sanitization of SQL characters and commands could also contribute to a SQL injection vulnerability.

Mozilla. (2025, December 22).  *HTML: HyperText Markup Language | MDN* . https://developer.mozilla.org/en-US/docs/Web/HTML

* Mozilla's HTML documentation was frequently referenced for HTML syntax and input tag controls.

OWASP. (2024).  *Testing for insecure direct object references* . https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References

* The definition and examples of insecure direct object reference helped support the vulnerability overview in the proof-of-concept documentation.

OWASP. (2025).  *A04 Cryptographic Failures - OWASP Top 10:2025* . https://owasp.org/Top10/2025/A04_2025-Cryptographic_Failures/

* OWASP's Cryptographic Failures section of the Top Ten Web Application Vulnerabilities list discusses why fast hashing algorithms are insecure and have been deemed deprecated.

PlantUML. (n.d.).  *Information Engineering diagram syntax and features* . PlantUML.com. https://plantuml.com/ie-diagram

* PlantUML's documentation was referenced for demonstrating the relationships and their cardinality in the database objects.

Semgrep. (2026, April 28).  *Get started | Semgrep* . https://semgrep.dev/docs/getting-started/quickstart-ce

* Semgrep's documentation was relied upon to help create the scan command used to perform a static analysis scan on the codebase.

PortSwigger. (n.d.).  *What is CSRF (Cross-Site Request Forgery)? Tutorial & Examples | Web Security Academy* . https://portswigger.net/web-security/csrf

* This explanation of CSRF attacks helped support the description of this vulnerability in the CSRF overview section.

SQLite. (n.d.).  *The schema table* .https://www.sqlite.org/schematab.html

* This source was used to understand the SQLite schema table's structure to demonstrate database enumeration with the SQL injection proof-of-concept.

SQLite Tutorial. (2020, April 11).  *sqlite_version* . https://www.sqlitetutorial.net/sqlite-functions/sqlite_version/

* The documentation from SQLite's tutorial page was used to confirm the syntax of the sqlite_version() function for identifying the database type during the SQL injection proof-of-concept.

Steenbock, M. (2025). *CSC3020 Project Three* [Software].

* The validation logic for checking if an item has a valid quantity before being added to the cart or before the items in the card are purchased was modified for the Book Worm Application.

Steenbock, M. (2026). *CSC4028 Project One* [Software].

* Code from a previous project, specifically the implemented password policy, was re-adapted for the bookstore.

Stroz Friedberg. (2024).  *SF-password-research/rules/8-complex-1k.rule at main · strozfriedberg/sf-password-research* . GitHub. https://github.com/strozfriedberg/sf-password-research/blob/main/rules/8-complex-1k.rule

* This GitHub repository is where the rule list used in the weak cryptographic practices proof-of-concept was sourced.

The PHP Documentation Group. (n.d.).  *PHP: MD5 - manual* . https://www.php.net/manual/en/function.md5.php

* Although PHP was not used in the project, its MD5 documentation highlights the expected hexadecimal length of the return values from an MD5 hash.

The Python Wiki. (n.d.).  *MD5Passwords* . https://wiki.python.org/moin/Md5Passwords

* This wiki entry details how to use Python's hashlib module for MD5 hashing. It also demonstrates how to combine the salt with the hash within the MD5 function.

Van. (2012, April 13). *How to set the foreign key to a default value on delete?* Stack Overflow. https://stackoverflow.com/questions/10142066/how-to-set-the-foreign-key-to-a-default-value-on-delete

* The guidance from the reply post helped craft the Cart and Invoice models to manage the user id if the user was deleted while keeping the cart and invoice objects valid in the database.

Weakpass. (n.d.).  *RockYou Wordlist* . https://weakpass.com/wordlists/rockyou.txt#wordlist

* This website contains the dictionary list used in the password cracking demonstration that was part of the weak cryptographic practices proof-of-concept.

Zap Dev Team. (n.d.).  *ZAP – Getting started* . https://www.zaproxy.org/getting-started/

* OWASP ZAP's documentation was used to help set up the tool and execute a DAST scan on the application.
