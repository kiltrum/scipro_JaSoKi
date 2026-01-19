import base64
from pathlib import Path

def _img_to_data_uri(png_path: Path) -> str:
    data = png_path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"

def build_html(plot1, plot2, plot3, date):
    # project root is current working directory when you run era5vis_clim
    cwd = Path.cwd()
    outdir = cwd / "html"
    outdir.mkdir(exist_ok=True)

    fname = f"ERA5_mean_anomaly_sounding_crosssection_{date}.html"
    outpath = outdir / fname

    png_dir = cwd / "PNG"
    p1 = png_dir / plot1
    p2 = png_dir / plot2
    p3 = png_dir / plot3

    # Hard fail early if any PNG is missing
    for p in (p1, p2, p3):
        if not p.is_file():
            raise FileNotFoundError(f"Missing PNG file: {p}")

    img1 = _img_to_data_uri(p1)
    img2 = _img_to_data_uri(p2)
    img3 = _img_to_data_uri(p3)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ERA5 visualisation {date}</title>
  <style>
    body {{ font-family: Arial, sans-serif; padding: 20px; }}
    .row {{ display: flex; gap: 20px; justify-content: center; margin-bottom: 30px; }}
    img {{ max-width: 100%; height: auto; border: 1px solid #ccc; }}
    .half img {{ width: 45%; }}
    .full img {{ width: 95%; }}
  </style>
</head>
<body>

<h2>ERA5 visualisation – {date}</h2>

<div class="row half">
  <img src="{img1}" alt="Map anomaly">
  <img src="{img2}" alt="Sounding">
</div>

<div class="row full">
  <img src="{img3}" alt="Cross-section">
</div>

</body>
</html>
"""

    outpath.write_text(html, encoding="utf-8")
    print(f"HTML saved to: {outpath}")
    return str(outpath)