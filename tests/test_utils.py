import bitly
import utils
import config


def test_bitly():
    assert bitly.bitly("https://wsj.com")


def test_capitalization():
    if config.Config.smart_cap_preference:
        assert utils.capitalize_title("this is a title") == "This Is a Title"
    elif not config.Config.smart_cap_preference:
        assert utils.capitalize_title("this is a title") == "This Is A Title"
