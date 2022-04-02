# Setup

```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
pre-commit install
```

# Run locally

```
python main.py
```

Then, you can hit one of the urls directly through your browser, `wget`, `curl`, or your preferred method.

# Create on Heroku

```
heroku login
heroku create <app_name>
heroku config:set APP_LOCATION=heroku
```