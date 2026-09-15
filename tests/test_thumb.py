from product.models import thumb, unthumb


def test_thumb_resizes_s3_originals():
    url = "https://cocciphoto.s3.eu-central-1.amazonaws.com/cocciarchivio/1753286228212_0.png"
    out = thumb(url)
    assert out.startswith("https://wsrv.nl/?url=cocciphoto.s3")
    assert "&w=1000&output=webp" in out
    assert "https://" not in out[len("https://wsrv.nl/?url=") :]  # scheme stripped once


def test_thumb_passes_through_empty_and_non_https():
    assert thumb("") == ""
    assert thumb(None) is None
    assert thumb("/media/images/logo.svg") == "/media/images/logo.svg"


def test_thumb_is_idempotent():
    url = "https://cocciphoto.s3.eu-central-1.amazonaws.com/cocciarchivio/1753286228212_0.png"
    assert thumb(thumb(url)) == thumb(url)


def test_unthumb_recovers_the_original():
    url = "https://cocciphoto.s3.eu-central-1.amazonaws.com/cocciarchivio/1753286228212_0.png"
    assert unthumb(thumb(url)) == url
    assert unthumb(url) == url
    assert unthumb("") == ""
