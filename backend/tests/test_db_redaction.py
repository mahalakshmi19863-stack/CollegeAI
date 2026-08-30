from backend.app.database.mongodb import redact_mongodb_uri


def test_redact_mongodb_uri_hides_credentials():
    uri = "mongodb+srv://demo_user:super_secret@cluster0.example.mongodb.net/?appName=Cluster0"

    redacted = redact_mongodb_uri(uri)

    assert "demo_user" not in redacted
    assert "super_secret" not in redacted
    assert "***" in redacted
    assert "cluster0.example.mongodb.net" in redacted
