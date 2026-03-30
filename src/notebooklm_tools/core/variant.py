"""Variant configuration for standard vs enterprise NotebookLM.

Auto-detects the variant from the NOTEBOOKLM_BASE_URL environment variable.
Enterprise (Gemini Enterprise / NotebookLM Pro) uses a different domain,
URL structure, and file upload API compared to the standard personal version.
"""

import os
from dataclasses import dataclass

from notebooklm_tools.utils.config import get_base_url


@dataclass(frozen=True)
class Variant:
    """Immutable configuration for a NotebookLM variant (standard or enterprise)."""

    name: str
    base_url: str
    ui_name: str
    path_prefix: str
    bl_fallback: str
    query_service: str
    max_sources: int
    upload_domain: str | None
    unsupported_studio_types: frozenset[str]

    @property
    def batchexecute_path(self) -> str:
        return f"{self.path_prefix}_/{self.ui_name}/data/batchexecute"

    @property
    def query_endpoint(self) -> str:
        return f"{self.path_prefix}_/{self.ui_name}/data/{self.query_service}"

    @property
    def auth_page_path(self) -> str:
        """Path for CSRF token extraction page.

        For enterprise, this must point to the NotebookLM iframe page (not the
        Gemini Enterprise shell). Requires project, origin, refCid, authuser
        params so the page loads the NotebookLM app with correct tokens.
        """
        if self.name != "enterprise":
            return self.path_prefix
        import urllib.parse

        params: dict[str, str] = {}
        project_id = os.environ.get("NOTEBOOKLM_PROJECT_ID", "")
        cid = os.environ.get("NOTEBOOKLM_CID", "")
        if project_id:
            params["project"] = project_id
        params["origin"] = self.base_url
        if cid:
            params["refCid"] = cid
        params["hl"] = os.environ.get("NOTEBOOKLM_HL", "en_US")
        params["authuser"] = "0"
        return f"{self.path_prefix}?{urllib.parse.urlencode(params)}"

    def notebook_source_path(self, notebook_id: str) -> str:
        return f"{self.path_prefix}notebook/{notebook_id}"

    @property
    def is_enterprise(self) -> bool:
        return self.name == "enterprise"


def _make_standard_variant(base_url: str) -> Variant:
    return Variant(
        name="standard",
        base_url=base_url,
        ui_name="LabsTailwindUi",
        path_prefix="/",
        bl_fallback="boq_labs-tailwind-frontend_20260108.06_p0",
        query_service=(
            "google.internal.labs.tailwind.orchestration.v1."
            "LabsTailwindOrchestrationService/GenerateFreeFormStreamed"
        ),
        max_sources=50,
        upload_domain=None,
        unsupported_studio_types=frozenset(),
    )


def _make_enterprise_variant(base_url: str) -> Variant:
    return Variant(
        name="enterprise",
        base_url=base_url,
        ui_name="CloudNotebookLmUi",
        path_prefix="/notebooklm/global/",
        bl_fallback="boq_cloud-ml-notebooklm-ui_20260324.07_p0",
        query_service=(
            "google.cloud.notebooklm.v1main."
            "NotebookService/GenerateFreeFormStreamed"
        ),
        max_sources=300,
        upload_domain="discoveryengine.clients6.google.com",
        unsupported_studio_types=frozenset({
            "flashcards",
            "infographic",
            "slide_deck",
            "data_table",
        }),
    )


_cached_variant: Variant | None = None


def get_variant() -> Variant:
    """Get the current variant configuration (cached).

    Auto-detects enterprise from the base URL. The variant is cached after
    the first call. Use reset_variant() to clear the cache (e.g. in tests).
    """
    global _cached_variant
    if _cached_variant is not None:
        return _cached_variant

    base_url = get_base_url()
    if "vertexaisearch.cloud.google.com" in base_url:
        _cached_variant = _make_enterprise_variant(base_url)
    else:
        _cached_variant = _make_standard_variant(base_url)
    return _cached_variant


def get_project_id() -> str:
    """Get the enterprise project ID from env var or empty string.

    Required for enterprise file upload via Discovery Engine API.
    Can also be auto-extracted from the page HTML during CSRF refresh.
    """
    return os.environ.get("NOTEBOOKLM_PROJECT_ID", "")


def get_customer_id() -> str:
    """Get the enterprise customer/organization ID (cid) from env var or empty string.

    This is the UUID in the Gemini Enterprise URL:
        .../home/cid/79e69e06-91db-410c-8426-98f01f2098ab

    Used to construct the correct auth page URL and CDP login URL
    so the browser navigates to the right organization context.
    Set via NOTEBOOKLM_CID env var.
    """
    return os.environ.get("NOTEBOOKLM_CID", "")


def reset_variant() -> None:
    """Reset the cached variant (for testing)."""
    global _cached_variant
    _cached_variant = None


# =========================================================================
# Enterprise RPC ID mapping (standard → enterprise)
# =========================================================================

# Maps standard RPC IDs to their enterprise equivalents.
# Only RPCs that differ are listed — unlisted RPCs are assumed identical
# (or unsupported) in enterprise.
_ENTERPRISE_RPC_MAP: dict[str, str] = {
    # Notebook operations
    "wXbhsf": "rG2vCb",   # list_notebooks (y2DRud is account/settings)
    "CCqFvf": "AzXHBd",   # create_notebook
    "rLM1Ne": "tHcQ6c",   # get_notebook
    "s0tc2d": "aja7m",    # rename_notebook (shared with chat_configure)
    "WWINqb": "J0zsyb",   # delete_notebook
    # Source operations
    "izAoDd": "kqBlec",   # add_source (URL, text, Drive, research import)
    "hizoJc": "GcP14b",   # get_source
    "b7Wfje": "DaIlK",    # rename_source
    "tGMBJ": "iMJYGb",    # delete_source
    # Chat / Query
    "hT54vc": "aja7m",    # chat_configure (shared with rename_notebook)
    # Studio operations
    "R7cb6c": "aNc62",    # create_studio (audio + video)
    "yyryJe": "IU9Pxb",   # generate (mind_map, briefing_doc, etc.)
    "CYK0Xb": "YoTKpc",   # save_mind_map / create_note
    "gArtLc": "a0XDpc",   # poll_studio_status
    "VfAZjd": "LmGGPd",   # get_summary / list_notes
    "V5N4be": "ZMz0Qe",   # delete_artifact
    # Note operations
    "cFji9": "LmGGPd",    # list_notes (same as get_summary)
    "cYAfTb": "bpv8Yd",   # update_note
    "AH0mwd": "ZMz0Qe",   # delete_note (same as delete_artifact)
    # Sharing
    "JFMDGd": "LJ9a9c",   # get_share_status
    "QDyure": "ugXkff",   # share_invite
    # Research
    "Ljjv0c": "YHCHrc",   # research_start
    "LBwxtb": "kqBlec",   # research_import (same as add_source)
}


def translate_rpc_id(standard_id: str) -> str:
    """Translate a standard RPC ID to enterprise if in enterprise mode.

    Returns the enterprise RPC ID when running against enterprise, or
    the original ID unchanged for standard.
    """
    v = get_variant()
    if not v.is_enterprise:
        return standard_id
    return _ENTERPRISE_RPC_MAP.get(standard_id, standard_id)


# =========================================================================
# Enterprise resource path helpers
# =========================================================================


def resource_prefix() -> str:
    """Build the Discovery Engine resource prefix: projects/{pid}/locations/global.

    Required for enterprise params. Returns empty string for standard variant.
    """
    pid = get_project_id()
    if not pid:
        return ""
    return f"projects/{pid}/locations/global"


def notebook_resource(notebook_id: str) -> str:
    """Build full notebook resource path for enterprise."""
    return f"{resource_prefix()}/notebooks/{notebook_id}"


def source_resource(notebook_id: str, source_id: str) -> str:
    """Build full source resource path for enterprise."""
    return f"{resource_prefix()}/notebooks/{notebook_id}/sources/{source_id}"


def note_resource(notebook_id: str, note_id: str) -> str:
    """Build full note resource path for enterprise."""
    return f"{resource_prefix()}/notebooks/{notebook_id}/notes/{note_id}"


def wrap_70000(resource_path: str) -> dict[str, str]:
    """Wrap a resource path in the enterprise {"70000": path} format."""
    return {"70000": resource_path}


def wrap_70001(cid: str) -> dict[str, str]:
    """Wrap a customer/org ID in the enterprise {"70001": cid} format."""
    return {"70001": cid}
