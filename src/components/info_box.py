import dash_mantine_components as dmc
from dash_iconify import DashIconify


def info_box(paragraphs, title="About this page"):
    """Collapsible, page-level help callout.

    `paragraphs` is a list of blocks: plain strings are rendered as
    separate `dmc.Text` paragraphs with consistent spacing; any other
    Dash component (e.g. `html.Ul`) is passed through as-is.
    Styled via the `.info-box` rules in assets/bootstrap.css.
    """
    if not isinstance(paragraphs, list):
        paragraphs = [paragraphs]
    blocks = [
        dmc.Text(block, size="sm") if isinstance(block, str) else block
        for block in paragraphs
    ]
    return dmc.Accordion(
        variant="contained",
        radius="md",
        className="mb-3 info-box",
        children=[
            dmc.AccordionItem(
                value="help",
                children=[
                    dmc.AccordionControl(
                        title,
                        icon=DashIconify(icon="ion:information-circle", width=22),
                    ),
                    dmc.AccordionPanel(
                        dmc.Stack(blocks, gap="xs"),
                    ),
                ],
            )
        ],
    )
