# MCP-style tools (public slice)

The planning agent reads the world model through **named tools**, not by dumping the graph.

```text
list_object_types
  -> inspect_object_type
    -> lookup_object
      -> walk_link
    -> search_objects
        -> preview_action
```

| Tool | Arguments | Maps to |
| --- | --- | --- |
| `list_object_types` | — | Object type list |
| `inspect_object_type` | `objectType` | Properties + incident link types |
| `lookup_object` | `objectType`, `objectId` | `GET /api/objects/{type}/{id}` |
| `walk_link` | `objectType`, `objectId`, `linkType` | `GET /api/objects/{type}/{id}/walk/{linkType}` |
| `preview_action` | `actionId`, `objectId` | `POST /api/actions/preview` |
| `search_objects` | `query`, optional `objectType` | `GET /api/search?q=` · substring scan |

`GET /api/mcp/tools` is the catalog. `POST /api/mcp/call` runs one tool.

This is **not** a GitLab mirror of the internal SCP Metadata MCP (no IPS module/model APIs, no live scenarios, no WeKnora chat). The idea is the same: the agent names a tool, then reads a typed fact.
