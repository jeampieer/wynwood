from pathlib import Path


def test_readme_documents_checkout_registration_and_mock_payment():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "registro manual de un usuario nuevo ocurre dentro del checkout" in readme.lower()
    assert "mock de pasarela" in readme.lower()
    assert "Payment" in readme
    assert "paid" in readme
