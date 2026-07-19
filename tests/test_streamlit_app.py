import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_streamlit_app_renders_and_updates_scenario() -> None:
    app = AppTest.from_file(PROJECT_ROOT / "app.py", default_timeout=30).run()
    assert not app.exception
    assert [tab.label for tab in app.tabs] == [
        "Dein Mietbild",
        "Marktverlauf",
        "Methodik & Quellen",
    ]
    assert app.selectbox[0].value == "Berlin"
    styles = next(
        markdown.value
        for markdown in app.markdown
        if '[data-testid="stHeaderActionElements"]' in markdown.value
    )
    assert '.hero [data-testid="stHeaderActionElements"]' in styles
    hero = next(markdown.value for markdown in app.markdown if 'class="hero"' in markdown.value)
    assert "Was kostet Wohnen in Berlin" in hero
    model_chart = json.loads(app.get("plotly_chart")[4].proto.spec)
    assert "7 Modellfamilien" in model_chart["layout"]["title"]["text"]

    app.selectbox[0].select("Hamburg")
    app.slider[0].set_value(90)
    app.run()

    assert not app.exception
    assert app.selectbox[0].value == "Hamburg"
    assert app.slider[0].value == 90
    updated_hero = next(
        markdown.value for markdown in app.markdown if 'class="hero"' in markdown.value
    )
    assert "Was kostet Wohnen in Hamburg" in updated_hero
