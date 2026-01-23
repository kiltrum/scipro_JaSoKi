from pathlib import Path
import pytest
from era5vis.build_html import build_html  

def test_build_html_embeds_pngs(monkeypatch, tmp_path):
    #set up dummy PNG files and current working directory
    monkeypatch.chdir(tmp_path)

    png_dir = tmp_path / "PNG"
    png_dir.mkdir()

    for name in ("a.png", "b.png", "c.png"):
        (png_dir / name).write_bytes(b"fakepng")

    # _img_to_data_uri mocken 
    import era5vis.build_html as build_html_mod


    def fake_img_to_data_uri(path):
        return "data:image/png;base64,FAKE"

    monkeypatch.setattr(
        build_html_mod,
        "_img_to_data_uri",
        fake_img_to_data_uri
    )

    #run the function we want to test    
    outpath = build_html(
        "a.png",
        "b.png",
        "c.png",
        date="20240101"
    )

    outpath = Path(outpath)

    #test for solutions
    assert outpath.exists()
    assert outpath.parent.name == "html"
    assert outpath.suffix == ".html"

    content = outpath.read_text()

    assert content.count("data:image/png;base64,FAKE") == 3
    assert "20240101" in content
