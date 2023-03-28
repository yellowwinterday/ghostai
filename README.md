# Ghost Blog Relationship

## Requirements

- Python 3.7.1+

In general, we want to support the versions of Python that our
customers are using. Lower version may leads to openAI dependencies install failure.
## Installation

Make sure the following packages are installed before start the script.
```bash
pip install --upgrade pip
pip install openai pandas matplotlib scipy scikit-learn plotly pyjwt
```

## Usage

The library needs to be configured with your account's secret key.
OpenAI API Key is available on the [website](https://platform.openai.com/account/api-keys). 

Ghost Admin API Key can be found by following instructions here: [website](https://ghost.org/docs/admin-api/#token-authentication)
  
Either set it as the `OPENAI_API_KEY` & `GHOST_ADMIN_API_KEY` environment variable before using the library:

```bash
export OPENAI_API_KEY='sk-...'
export GHOST_API_KEY='...'

```

Or set `OPENAI_API_KEY` & `GHOST_ADMIN_API_KEY` to `./.env`:

```python
[BASIC]
GHOST_ADMIN_API_KEY={YOUR_GHOST_ADMIN_API_KEY}
GHOST_SITE_URL={YOUR_BLOG_SITE_URL}
OPENAI_API_KEY={YOUR_OPENAI_API_KEY}
EMBEDDING_OUTPUT_PATH=./output
MAX_RELATED_BLOG_COUNT=20
```

After all set, start the script as following:
```sh
python ghost_relation_tags.py

```

