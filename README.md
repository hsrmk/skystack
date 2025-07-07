## Tests

Run individual tests using:

```
pytest -s -vv test/test_newsletter.py
```

Run all tests using:

```
python3 run_tests.py
```

## AT Proto Wikis Search

https://deepwiki.com/bluesky-social/atproto

https://deepwiki.com/search/how-to-create-an-account-on-a_72d896ba-889d-462c-a3bd-f60f70d9be79

https://deepwiki.com/search/on-createaccount-is-there-a-li_e9170255-c396-4c1a-8d1c-b5f9ae5e71f4

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
