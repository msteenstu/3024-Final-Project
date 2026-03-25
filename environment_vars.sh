export FLASK_APP=src/app
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex())')"
flask run