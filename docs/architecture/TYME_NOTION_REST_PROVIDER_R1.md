# R1 native Notion provider (candidate)

Baseline: `0af29cf783e0cf5a515ba2978fcf209a600d1f24`.
This adds a provider to the merged R1 reader and collector, not a new ontology.
R2 classification, context admission, and R3 Attention remain outside scope.

The native API supplies the evidence missing from the ChatGPT connector probe:
`GET /v1/users/me` for bot identity, `GET /v1/pages/{id}` for native page/parent metadata,
`GET /v1/pages/{id}/markdown` for enhanced Markdown plus completeness signals, and
`GET /v1/blocks/{root}/children` for native child_page membership plus has_more/next_cursor.

The provider is GET-only, fixed to api.notion.com, pinned to Notion-Version 2026-03-11,
bounded by call/byte/time limits, performs no retries or search, and preserves successful
raw JSON responses in a private sidecar. It never derives membership from Markdown,
titles, mentions, links, or model inference.

Use a separately provisioned Notion internal connection with Read content only, grant it
the Horizon root, and store the secret as NOTION_API_TOKEN in the runtime secret store.
Do not paste the token into chat, code, logs, or Notion. The ChatGPT Notion connection is
not automatically a Python API credential.

A live run is explicit only:
```sh
python -m adapters.tyme_notion_rest_provider_v0 \
  --root 38cc51d5-4b75-8187-b66f-c5f9f0032501 \
  --output-dir /private/captures/horizon-r1-new
```

The output directory must be new and private. It contains acquisition.json,
transport.json, and receipt.json. Exit 0 means complete acquisition requiring review,
not institutional acceptance. R2/R3 remain closed until a credentialed Horizon run,
offline replay, and semantic review complete.

Official references:
- https://developers.notion.com/reference/get-block-children
- https://developers.notion.com/reference/retrieve-page-markdown
- https://developers.notion.com/reference/retrieve-a-page
- https://developers.notion.com/reference/get-self
- https://developers.notion.com/guides/get-started/internal-connections
- https://developers.notion.com/reference/request-limits
