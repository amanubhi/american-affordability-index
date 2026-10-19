from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]

def test_all_streamlit_pages_and_simulator():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=45).run()
    assert not app.exception
    for page in ['State Housing','Cost Breakdown','Simulator']:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, str(app.exception)
    before=app.metric[2].value
    app.slider[1].set_value(20.).run()
    assert not app.exception
    assert app.metric[2].value!=before
