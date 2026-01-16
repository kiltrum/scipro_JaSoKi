
import os

def build_html(plot1, plot2, date):
    outdir = "html"

    fname = f"ERA5_mean_anomaly_and_sounding_{date}.html"

    if not os.path.isdir(outdir):
        os.makedirs(outdir)
        print(f"Created output directory: {outdir}")
    else:
        print(f"Output directory already exists: {outdir}")

    outpath = os.path.join(outdir, fname)

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            display: flex;
            gap: 20px;
            justify-content: center;
            align-items: flex-start;
        }}
        img {{
            max-width: 45%;
            height: auto;
        }}
    </style>
</head>
<body>

    <div class="container">
        <img src="../PNG/{plot1}" alt="Plot 1">
        <img src="../PNG/{plot2}" alt="Plot 2">
    </div>

</body>
</html>
"""

    with open(outpath, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML saved to: {outpath}")



