import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestListTemplates:
    def test_list_templates_returns_12_entries(self):
        res = client.get("/api/templates/")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) == 12
        for item in data:
            assert "name" in item


class TestGetTemplateContent:
    def test_get_mutual_nda_content_returns_200(self):
        res = client.get("/api/templates/mutual-non-disclosure-agreement/content")
        assert res.status_code == 200
        content = res.text
        assert len(content) > 0
        assert "Non-Disclosure" in content

    def test_get_unknown_template_returns_404(self):
        res = client.get("/api/templates/unknown-doc/content")
        assert res.status_code == 404
