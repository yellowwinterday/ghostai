# Ghost Blog Relationship

GhostAI Related Posts is a project that utilizes OpenAI Embedding API to generate related blog post tags for a given Ghost Blogging site. The project provides the functionality to display "Related Posts" at the bottom of each blog post. Currently, this feature is not available in Ghost.

The project comprises of two scripts that can be executed either on a local machine or directly on the server. Unless the site has tens of thousands of blog posts, running the scripts on a local machine should suffice.

The first script iterates through all public blog posts on the server and extracts the text content, which is then sent to the OpenAI (Ada model) to generate a set of vectors. These vectors are then stored in a text file. The script also supports incremental generation, which means that it only generates vectors for blog posts that have not yet been processed.

The second script iterates through all the vectors in the directory and ranks their similarity by giving a score. For each blog post, a few other blog posts with high similarity ranking will be grouped together. Ghost internal tagging feature is used for the grouping mechanism, and each blog post ID becomes the internal tag name.

To display the related blog posts at the bottom of another blog post, the post.hbs template needs to be edited by inserting a simple tag filter. This design works with both self-hosted Ghost sites and Ghost Pro sites (hosted by the Ghost team) and does not require any additional configuration, database changes, or other adjustments.

Users can contribute to the GhostAI Related Posts project by submitting pull requests on Github. We welcome any improvements to the project, including bug fixes, new features, and enhancements.

## Requirements

- Python 3.7.1+

To ensure compatibility with our customers' Python versions, we recommend using Python 3.7.1 or higher.

## Installation

Before starting the script, ensure that the following packages are installed:

```bash
pip install --upgrade pip
pip install openai pandas matplotlib scipy scikit-learn plotly pyjwt
```

## Usage

The library needs to be configured with your account's secret key. OpenAI API Key is available on the [website](https://platform.openai.com/account/api-keys). Ghost Admin API Key can be found by following instructions here: [website](https://ghost.org/docs/admin-api/#token-authentication)

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

After all set, start the script as follows:

```sh
python ghost_relation_tags.py

```

