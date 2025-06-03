import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import os
import webdriver_manager.microsoft as wm
if not hasattr(wm, "MsEdgeDriverManager"):
    wm.MsEdgeDriverManager = wm.EdgeChromiumDriverManager
import re
import app


def test_iniciar_scraping_creates_files(tmp_path, mocker):
    data = [
        {
            "valor": "R$ 100.000",
            "endereco": "Rua A, 123",
            "bairro": "Centro",
            "area": "50 m²",
            "quartos": "2 quartos",
            "banheiros": "1 banheiro",
            "vagas": "1 vaga",
            "link": "http://example.com/1",
        },
        {
            "valor": "R$ 200.000",
            "endereco": "Rua B, 456",
            "bairro": "Bairro B",
            "area": "100 m²",
            "quartos": "3 quartos",
            "banheiros": "2 banheiros",
            "vagas": "2 vagas",
            "link": "http://example.com/2",
        },
    ]

    class FakeElement:
        def __init__(self, text=""):
            self._text = text

        @property
        def text(self):
            return self._text

        def get_attribute(self, name):
            if name == "href":
                return self._text
            return None

    class FakeDriver:
        def get(self, url):
            pass

        def quit(self):
            pass

        def find_element(self, by, xpath):
            match = re.search(r"div\[(\d+)\]/div/div\[1\]/div\[2\]/div\[1\]/div\[1\]", xpath)
            if not match:
                raise Exception("not found")
            idx = int(match.group(1)) - 1
            if idx >= len(data):
                raise Exception("no element")
            if xpath.endswith("/div[1]/div/div/div/div[1]/div"):
                return FakeElement(data[idx]["valor"])
            if xpath.endswith("/div[2]/div/div"):
                return FakeElement(data[idx]["endereco"])
            if xpath.endswith("/div[2]/div/h2"):
                return FakeElement(data[idx]["bairro"])
            if xpath.endswith("/div[3]/h3/span[1]"):
                return FakeElement(data[idx]["area"])
            if xpath.endswith("/div[3]/h3/span[2]"):
                return FakeElement(data[idx]["quartos"])
            if xpath.endswith("/div[3]/h3/span[3]"):
                return FakeElement(data[idx]["banheiros"])
            if xpath.endswith("/div[3]/h3/span[4]"):
                return FakeElement(data[idx]["vagas"])
            if xpath.endswith("/h3/a"):
                return FakeElement(data[idx]["link"])
            raise Exception("unknown path")

    mocker.patch("app.webdriver.Edge", return_value=FakeDriver())
    mocker.patch("app.MsEdgeDriverManager", return_value=mocker.Mock(install=lambda: "driver"))
    mocker.patch("app.Service", lambda path: None)
    mocker.patch("time.sleep", lambda x: None)

    mocker.patch.object(app, "TEMP_DIR", str(tmp_path))
    os.makedirs(tmp_path, exist_ok=True)

    excel_path, csv_path = app.iniciar_scraping("http://test", "result")

    assert os.path.exists(excel_path)
    assert os.path.exists(csv_path)
    assert str(tmp_path) in excel_path
    assert str(tmp_path) in csv_path
