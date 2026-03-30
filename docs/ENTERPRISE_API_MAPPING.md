# Enterprise API Mapping (NotebookLM Pro / Gemini Enterprise)

Complete reverse-engineered mapping between standard and enterprise NotebookLM APIs.

- Enterprise base: `https://vertexaisearch.cloud.google.com`
- Enterprise batchexecute: `/notebooklm/global/_/CloudNotebookLmUi/data/batchexecute`
- Resource prefix (rp): `projects/{project_id}/locations/global`
- Notebook resource: `{rp}/notebooks/{notebook_id}`
- Source resource: `{rp}/notebooks/{notebook_id}/sources/{source_id}`
- Note resource: `{rp}/notebooks/{notebook_id}/notes/{note_id}`

## Key Architecture Difference

Standard API uses raw IDs. Enterprise wraps everything in Discovery Engine resource paths.
Enterprise also uses `{"70000": "{resource_path}"}` or `{"70001": "{cid}"}` wrappers.

## Complete RPC ID Mapping

### Notebook Operations

| Operation | Standard | Enterprise | Enterprise Params |
|-----------|----------|-----------|-------------------|
| list_notebooks | `wXbhsf` | `y2DRud` | `["{rp}"]` |
| create_notebook | `CCqFvf` | `AzXHBd` | `["{rp}", ["", null, null, null, null, [null, null, null, null, null, null, 1]]]` |
| get_notebook | `rLM1Ne` | `tHcQ6c` | `["{rp}/notebooks/{nb_id}"]` |
| rename_notebook | `s0tc2d` | `aja7m` | `[["New Title", {"70000": "{rp}/notebooks/{nb_id}"}], [["title", "emoji"]]]` |
| delete_notebook | `WWINqb` | `J0zsyb` | `["{rp}", ["{rp}/notebooks/{nb_id}"]]` |

### Source Operations

| Operation | Standard | Enterprise | Enterprise Params |
|-----------|----------|-----------|-------------------|
| add_source (URL) | `izAoDd` | `kqBlec` | `["{rp}/notebooks/{nb_id}", [[null, null, ["{url}"], null, null, null, null, null, null, null, 1]]]` |
| add_source (text) | `izAoDd` | `kqBlec` | `["{rp}/notebooks/{nb_id}", [[null, ["Title", "Content"], null, 2, null, null, null, null, null, null, 1]]]` |
| add_source (research import) | `izAoDd` | `kqBlec` | Same as URL but last flag = `2` instead of `1` |
| get_source | `hizoJc` | `GcP14b` | `["{rp}/notebooks/{nb_id}/sources/{src_id}", [["{src_id}"]]]` |
| rename_source | `b7Wfje` | `DaIlK` | `[[null, "New Name", {"70000": "{rp}/notebooks/{nb_id}/sources/{src_id}"}], [["title"]]]` |
| delete_source | `tGMBJ` | `iMJYGb` | `["{rp}/notebooks/{nb_id}", ["{rp}/notebooks/{nb_id}/sources/{src_id}"]]` |

### Chat / Query

| Operation | Standard | Enterprise | Enterprise Params |
|-----------|----------|-----------|-------------------|
| streaming query | gRPC `LabsTailwindOrchestrationService` | gRPC `NotebookService` | `[null, "[[src_ids], \"question\", {\"70000\": \"{rp}/notebooks/{nb_id}\"}]"]` |
| chat_configure | `hT54vc` | `aja7m` | `[[null, null, null, null, null, null, null, [[goal_code], []], {"70000": "{rp}/notebooks/{nb_id}"}], [["advanced_settings"]]]` |

Note: `aja7m` is shared between rename_notebook and chat_configure — the `[["field_name"]]` suffix determines which field is updated.

### Studio Operations

| Operation | Standard | Enterprise | Enterprise Params |
|-----------|----------|-----------|-------------------|
| create_studio (audio) | `R7cb6c` | `aNc62` | `[[2], "{nb_id}", [..., 1, [src_ids], ...], {"70000": "{rp}/notebooks/{nb_id}"}]` (type=1) |
| create_studio (video) | `R7cb6c` | `aNc62` | Same structure, type=3 |
| generate (mind_map) | `yyryJe` | `IU9Pxb` | `[[src_ids], null, null, null, null, ["interactive_mindmap", [["[CONTEXT]"]]], {"70000": "{rp}/notebooks/{nb_id}"}]` |
| generate (briefing_doc) | `yyryJe` | `IU9Pxb` | Same structure, type_string=`"briefing_doc"` |
| generate (study_guide) | `yyryJe` | `IU9Pxb` | Same structure, type_string=`"study_guide"` (inferred) |
| generate (faq) | `yyryJe` | `IU9Pxb` | Same structure, type_string=`"faq"` (inferred) |
| generate (timeline) | `yyryJe` | `IU9Pxb` | Same structure, type_string=`"timeline"` (inferred) |
| save_mind_map | `CYK0Xb` | `YoTKpc` | `["{rp}/notebooks/{nb_id}", [null, "{json}", [2, null, null, 5, [src_ids]], [], "Title"]]` |
| poll_studio_status | `gArtLc` | `a0XDpc` | `["{rp}/notebooks/{nb_id}"]` or with timestamp `[..., null, [ts_s, ts_ns]]` |
| get_summary | `VfAZjd` | `LmGGPd` | `["{rp}/notebooks/{nb_id}", [2]]` |
| get_audio_overview | N/A | `aKrKnb` | `["{rp}/notebooks/{nb_id}/audioOverviews/default", 0, [2]]` |
| delete_artifact | `V5N4be` | `ZMz0Qe` | `["{rp}/notebooks/{nb_id}", ["{rp}/notebooks/{nb_id}/notes/{artifact_id}"], ["{artifact_id}"]]` |

### Note Operations

| Operation | Standard | Enterprise | Enterprise Params |
|-----------|----------|-----------|-------------------|
| create_note | `CYK0Xb` | `YoTKpc` | `["{rp}/notebooks/{nb_id}", [null, "", [1], [], "New Note"]]` |
| update_note | `cYAfTb` | `bpv8Yd` | `[[null, "<p>content</p>", null, [], "Title", {"70000": "{rp}/notebooks/{nb_id}/notes/{note_id}"}], [["content", "title", "saved_response_data"]]]` |
| delete_note | `AH0mwd` | `ZMz0Qe` | `["{rp}/notebooks/{nb_id}", ["{rp}/notebooks/{nb_id}/notes/{note_id}"], ["{note_id}"]]` |
| list_notes | `cFji9` | `LmGGPd` | Likely same as get_summary — inferred, shares RPC |

### Sharing

| Operation | Standard | Enterprise | Enterprise Params |
|-----------|----------|-----------|-------------------|
| get_share_status | `JFMDGd` | `LJ9a9c` | `["{rp}/notebooks/{nb_id}"]` |
| share_invite | `QDyure` | `ugXkff` | `["{rp}/notebooks/{nb_id}", [["email", null, 3]], 1, [0, ""], {"70001": "{cid}"}]` |

Note: Role code 3 = Viewer in the share_invite params.

### Research / Discover

| Operation | Standard | Enterprise | Enterprise Params |
|-----------|----------|-----------|-------------------|
| research_start | `Ljjv0c` | `YHCHrc` | `[["query", 1], null, 1, "{nb_id}", {"70000": "{rp}/notebooks/{nb_id}"}]` |
| research_poll | `e3bVqc` | N/A | Enterprise research returns results synchronously in the start response |
| research_import | `LBwxtb` | `kqBlec` | Same as add_source (URL) with last flag = `2` |

### Other Enterprise RPCs

| Enterprise RPC | Purpose | Params |
|---------------|---------|--------|
| `rG2vCb` | settings/preferences polling | `["{rp}", null, null, 1]` |
| `ca0cne` | notebook context init | `[[2], "{nb_id}", {"70000": "{rp}/notebooks/{nb_id}"}]` |

### File Upload

| Component | Standard | Enterprise |
|-----------|---------|-----------|
| Register | RPC `o4cbdc` via batchexecute (step 1) | **Not needed** — no batchexecute registration |
| Upload init | POST `{base}/upload/_/` (step 2) | POST `https://discoveryengine.clients6.google.com/upload/v1alpha/projects/{project_id}/locations/global/notebooks/{notebook_id}/sources:uploadFile` |
| Upload data | PUT to returned URL (step 3) | PUT to `?upload_id=...&upload_protocol=resumable` |
| Protocol | 3-step: register RPC → init upload → stream data | 2-step: init upload → stream data (no batchexecute registration needed) |

Confirmed: enterprise file upload goes directly to Discovery Engine API with resumable upload protocol. No batchexecute RPC is involved in the upload process.

### Streaming Query Endpoint

| Variant | Endpoint Path |
|---------|--------------|
| Standard | `/_/LabsTailwindUi/data/google.internal.labs.tailwind.orchestration.v1.LabsTailwindOrchestrationService/GenerateFreeFormStreamed` |
| Enterprise | `/notebooklm/global/_/CloudNotebookLmUi/data/google.cloud.notebooklm.v1main.NotebookService/GenerateFreeFormStreamed` |

## Patterns Summary

1. **All IDs → resource paths**: `notebook_id` → `projects/{pid}/locations/global/notebooks/{id}`
2. **70000 wrapper**: `{"70000": "{resource_path}"}` used for notebook/source/note context
3. **70001 wrapper**: `{"70001": "{cid}"}` used for organization context (sharing)
4. **Unified RPCs**: Enterprise consolidates some operations:
   - `kqBlec` = all source additions (URL, text, Drive, research import)
   - `aNc62` = audio + video creation
   - `IU9Pxb` = all generated content (mind map, reports)
   - `YoTKpc` = save mind map + create note
   - `ZMz0Qe` = delete notes + delete artifacts
   - `aja7m` = rename notebook + chat configure (field selector determines action)
5. **Synchronous research**: No polling needed — results return in the start response

## Coverage Status

| Category | Mapped | Remaining |
|----------|--------|-----------|
| Notebook CRUD | 5/5 ✅ | — |
| Source ops | 6/6 ✅ | — |
| Chat/Query | 2/2 ✅ | — |
| Studio | 7/7 ✅ | — |
| Notes | 3/3 ✅ | list (shares RPC with get_summary) |
| Sharing | 2/2 ✅ | — |
| Research | 2/2 ✅ | — |
| File upload | 1/1 ✅ | No registration RPC needed (direct Discovery Engine) |
| **Total** | **28/28** | **Complete** |
