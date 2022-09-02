import bitly
import utils


def test_bitly():
    assert bitly.bitly("https://wsj.com")


def test_capitalization():
    assert utils.capitalize_title("this is a title")
