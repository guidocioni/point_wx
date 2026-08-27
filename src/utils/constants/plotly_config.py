"""Plotly visualization configuration."""

images_config = {
    "toImageButtonOptions": {
        "format": "png",  # one of png, svg, jpeg, webp
        "height": 800,
        "width": 900,
        "scale": 1.5,
    },
    "modeBarButtonsToRemove": [
        "select",
        "lasso2d",
        "zoomIn",
        "zoomOut",
        "autoScale",
    ],
    "displaylogo": False,
    "responsive": True,
    "doubleClick": False
}
