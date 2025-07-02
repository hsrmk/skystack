## Tests

Run individual tests using:

```
pytest -s -vv test/test_newsletter.py
```

Run all tests using:

```
python3 run_tests.py
```

## AT Proto Wiki Search

https://deepwiki.com/search/how-to-create-an-account-on-a_72d896ba-889d-462c-a3bd-f60f70d9be79

## Activate Env

```
python3 -m venv .venv
source .venv/bin/activate
```

## Testing /createNewsletter endpoint

```
curl -N -X POST {CLOUD_RUN_ENDPOINT}/createNewsletter \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.noahpinion.blog/"}'
```
