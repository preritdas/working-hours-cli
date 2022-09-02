import bitly
import utils
import config


def test_bitly():
    assert bitly.bitly("https://wsj.com")


def test_capitalization():
    assert utils.capitalize_title("this is a title", method_force="smart") == "This Is a Title"
    assert utils.capitalize_title("this is a title", method_force="default") == "This Is A Title"
