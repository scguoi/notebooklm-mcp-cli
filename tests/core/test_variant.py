"""Tests for core/variant.py — variant detection and URL construction."""

import os
from unittest import mock

import pytest

from notebooklm_tools.core.variant import (
    Variant,
    get_customer_id,
    get_project_id,
    get_variant,
    notebook_resource,
    note_resource,
    reset_variant,
    resource_prefix,
    source_resource,
    translate_rpc_id,
    wrap_70000,
    wrap_70001,
)


@pytest.fixture(autouse=True)
def _reset():
    """Reset cached variant before and after each test."""
    reset_variant()
    yield
    reset_variant()


class TestVariantDetection:
    """Test auto-detection of standard vs enterprise variant."""

    def test_default_is_standard(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NOTEBOOKLM_BASE_URL", None)
            v = get_variant()
            assert v.name == "standard"
            assert v.base_url == "https://notebooklm.google.com"

    def test_standard_explicit(self):
        with mock.patch.dict(
            os.environ, {"NOTEBOOKLM_BASE_URL": "https://notebooklm.google.com"}
        ):
            v = get_variant()
            assert v.name == "standard"
            assert not v.is_enterprise

    def test_enterprise_detected(self):
        with mock.patch.dict(
            os.environ,
            {"NOTEBOOKLM_BASE_URL": "https://vertexaisearch.cloud.google.com"},
        ):
            v = get_variant()
            assert v.name == "enterprise"
            assert v.is_enterprise

    def test_enterprise_with_trailing_slash(self):
        with mock.patch.dict(
            os.environ,
            {"NOTEBOOKLM_BASE_URL": "https://vertexaisearch.cloud.google.com/"},
        ):
            v = get_variant()
            assert v.is_enterprise

    def test_variant_is_cached(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NOTEBOOKLM_BASE_URL", None)
            v1 = get_variant()
            v2 = get_variant()
            assert v1 is v2

    def test_reset_clears_cache(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NOTEBOOKLM_BASE_URL", None)
            v1 = get_variant()
            reset_variant()
            v2 = get_variant()
            assert v1 is not v2


class TestStandardVariant:
    """Test standard variant URL construction."""

    def test_batchexecute_path(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NOTEBOOKLM_BASE_URL", None)
            v = get_variant()
            assert v.batchexecute_path == "/_/LabsTailwindUi/data/batchexecute"

    def test_query_endpoint(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NOTEBOOKLM_BASE_URL", None)
            v = get_variant()
            assert "LabsTailwindOrchestrationService" in v.query_endpoint
            assert "GenerateFreeFormStreamed" in v.query_endpoint

    def test_auth_page_path(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NOTEBOOKLM_BASE_URL", None)
            v = get_variant()
            assert v.auth_page_path == "/"

    def test_notebook_source_path(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NOTEBOOKLM_BASE_URL", None)
            v = get_variant()
            assert v.notebook_source_path("abc-123") == "/notebook/abc-123"

    def test_no_unsupported_types(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NOTEBOOKLM_BASE_URL", None)
            v = get_variant()
            assert len(v.unsupported_studio_types) == 0

    def test_upload_domain_none(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NOTEBOOKLM_BASE_URL", None)
            v = get_variant()
            assert v.upload_domain is None


class TestEnterpriseVariant:
    """Test enterprise variant URL construction."""

    @pytest.fixture(autouse=True)
    def _set_enterprise(self):
        with mock.patch.dict(
            os.environ,
            {"NOTEBOOKLM_BASE_URL": "https://vertexaisearch.cloud.google.com"},
        ):
            yield

    def test_batchexecute_path(self):
        v = get_variant()
        assert v.batchexecute_path == "/notebooklm/global/_/CloudNotebookLmUi/data/batchexecute"

    def test_query_endpoint(self):
        v = get_variant()
        assert "CloudNotebookLmUi" in v.query_endpoint
        assert "NotebookService/GenerateFreeFormStreamed" in v.query_endpoint

    def test_auth_page_path(self):
        v = get_variant()
        # Enterprise auth page includes origin, hl, authuser query params
        assert v.auth_page_path.startswith("/notebooklm/global/")
        assert "origin=" in v.auth_page_path
        assert "authuser=0" in v.auth_page_path

    def test_notebook_source_path(self):
        v = get_variant()
        assert v.notebook_source_path("abc-123") == "/notebooklm/global/notebook/abc-123"

    def test_unsupported_studio_types(self):
        v = get_variant()
        assert "flashcards" in v.unsupported_studio_types
        assert "infographic" in v.unsupported_studio_types
        assert "slide_deck" in v.unsupported_studio_types
        assert "data_table" in v.unsupported_studio_types
        assert "audio" not in v.unsupported_studio_types

    def test_upload_domain(self):
        v = get_variant()
        assert v.upload_domain == "discoveryengine.clients6.google.com"

    def test_max_sources(self):
        v = get_variant()
        assert v.max_sources == 300

    def test_bl_fallback(self):
        v = get_variant()
        assert "cloud-ml-notebooklm-ui" in v.bl_fallback


class TestEnterpriseAuthPagePath:
    """Test enterprise auth page path with org context params."""

    def test_auth_page_with_project_and_cid(self):
        with mock.patch.dict(
            os.environ,
            {
                "NOTEBOOKLM_BASE_URL": "https://vertexaisearch.cloud.google.com",
                "NOTEBOOKLM_PROJECT_ID": "77341597043",
                "NOTEBOOKLM_CID": "79e69e06-91db-410c-8426-98f01f2098ab",
            },
        ):
            v = get_variant()
            path = v.auth_page_path
            assert "project=77341597043" in path
            assert "refCid=79e69e06-91db-410c-8426-98f01f2098ab" in path
            assert path.startswith("/notebooklm/global/?")

    def test_auth_page_without_params(self):
        with mock.patch.dict(
            os.environ,
            {"NOTEBOOKLM_BASE_URL": "https://vertexaisearch.cloud.google.com"},
        ):
            os.environ.pop("NOTEBOOKLM_PROJECT_ID", None)
            os.environ.pop("NOTEBOOKLM_CID", None)
            v = get_variant()
            # Even without project/CID, enterprise adds origin + hl + authuser
            assert v.auth_page_path.startswith("/notebooklm/global/?")
            assert "origin=" in v.auth_page_path

    def test_standard_auth_page_ignores_params(self):
        with mock.patch.dict(
            os.environ,
            {
                "NOTEBOOKLM_PROJECT_ID": "12345",
                "NOTEBOOKLM_CID": "abc-def",
            },
        ):
            os.environ.pop("NOTEBOOKLM_BASE_URL", None)
            v = get_variant()
            assert v.auth_page_path == "/"


class TestProjectId:
    """Test project ID retrieval."""

    def test_default_empty(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NOTEBOOKLM_PROJECT_ID", None)
            assert get_project_id() == ""

    def test_from_env(self):
        with mock.patch.dict(os.environ, {"NOTEBOOKLM_PROJECT_ID": "12345"}):
            assert get_project_id() == "12345"


class TestCustomerId:
    """Test customer/org ID retrieval."""

    def test_default_empty(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NOTEBOOKLM_CID", None)
            assert get_customer_id() == ""

    def test_from_env(self):
        with mock.patch.dict(
            os.environ,
            {"NOTEBOOKLM_CID": "79e69e06-91db-410c-8426-98f01f2098ab"},
        ):
            assert get_customer_id() == "79e69e06-91db-410c-8426-98f01f2098ab"


class TestVariantImmutability:
    """Test that Variant is truly frozen."""

    def test_cannot_mutate(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NOTEBOOKLM_BASE_URL", None)
            v = get_variant()
            with pytest.raises(AttributeError):
                v.name = "hacked"  # type: ignore[misc]


class TestRpcTranslation:
    """Test RPC ID translation for enterprise variant."""

    def test_standard_no_translation(self):
        """Standard variant returns IDs unchanged."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NOTEBOOKLM_BASE_URL", None)
            assert translate_rpc_id("wXbhsf") == "wXbhsf"
            assert translate_rpc_id("CCqFvf") == "CCqFvf"

    def test_enterprise_translates_known(self):
        """Enterprise variant translates known RPC IDs."""
        with mock.patch.dict(
            os.environ,
            {"NOTEBOOKLM_BASE_URL": "https://vertexaisearch.cloud.google.com"},
        ):
            assert translate_rpc_id("wXbhsf") == "rG2vCb"  # list_notebooks
            assert translate_rpc_id("CCqFvf") == "AzXHBd"  # create_notebook
            assert translate_rpc_id("R7cb6c") == "aNc62"  # create_studio
            assert translate_rpc_id("izAoDd") == "kqBlec"  # add_source

    def test_enterprise_passthrough_unknown(self):
        """Enterprise variant passes through unknown RPC IDs unchanged."""
        with mock.patch.dict(
            os.environ,
            {"NOTEBOOKLM_BASE_URL": "https://vertexaisearch.cloud.google.com"},
        ):
            assert translate_rpc_id("UNKNOWN_RPC") == "UNKNOWN_RPC"


class TestResourcePathHelpers:
    """Test enterprise resource path construction."""

    def test_resource_prefix(self):
        with mock.patch.dict(os.environ, {"NOTEBOOKLM_PROJECT_ID": "77341597043"}):
            assert resource_prefix() == "projects/77341597043/locations/global"

    def test_resource_prefix_empty(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NOTEBOOKLM_PROJECT_ID", None)
            assert resource_prefix() == ""

    def test_notebook_resource(self):
        with mock.patch.dict(os.environ, {"NOTEBOOKLM_PROJECT_ID": "123"}):
            assert notebook_resource("nb-abc") == "projects/123/locations/global/notebooks/nb-abc"

    def test_source_resource(self):
        with mock.patch.dict(os.environ, {"NOTEBOOKLM_PROJECT_ID": "123"}):
            result = source_resource("nb-abc", "src-def")
            assert result == "projects/123/locations/global/notebooks/nb-abc/sources/src-def"

    def test_note_resource(self):
        with mock.patch.dict(os.environ, {"NOTEBOOKLM_PROJECT_ID": "123"}):
            result = note_resource("nb-abc", "note-ghi")
            assert result == "projects/123/locations/global/notebooks/nb-abc/notes/note-ghi"

    def test_wrap_70000(self):
        assert wrap_70000("some/path") == {"70000": "some/path"}

    def test_wrap_70001(self):
        assert wrap_70001("cid-123") == {"70001": "cid-123"}
