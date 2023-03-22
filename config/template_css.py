import config.config as config

FONT_FAMILY = "Helvetica"

CARD_PADDING = "20px"
CARD_MARGIN = "5px"

BOX_PADDING = "20px"
BOX_MARGIN = "5px"

TOPBAR_PADDING_TOP = "15px"
TOPBAR_PADDING_SIDES = "40px"

FILTER_HEIGHT = "50px"

TABS_PADDING = "10px"
TABS_PADDING_SPACE = "300px"


TITLE = {
    "font-size": "25px",
    # "font-family": FONT_FAMILY,
    "vertical-align": "center",
    "margin-right": "20px",
    # "float":"left",

    "height": "100%"
}

TOPBAR = {
    "display": "flex",
    "flex-wrap": "wrap",
    "background": config.TOPBAR_COLOR,

    "width": "100vw",
    "padding-top": TOPBAR_PADDING_TOP,
    "padding-left": TOPBAR_PADDING_SIDES,
    "padding-right": TOPBAR_PADDING_SIDES,
}

TAB = {
    "background": config.TOPBAR_COLOR,
    "border": "none",
    "border-bottom": f"1px {config.TOPBAR_COLOR} solid",
    "padding": TABS_PADDING,
    "width": "fit-content",
    "height": "100%"
}

TAB_SELECTED = {
    "background": config.TOPBAR_COLOR,
    "border": "none",
    "padding": TABS_PADDING,
    # "padding-left": TABS_PADDING_SPACE,
    "color": config.TEXT_COLOR,
    # "font-family": FONT_FAMILY,
    "border-bottom": f"1px {config.TAB_SELECTED_BORDER} solid",
    "width": "fit-content",
    "height": "100%"
}

BODY = {
    "position": "absolute",
    "background": config.BACKGROUND_COLOR,

    "width": "100vw",
    "height": "100vh",

    "color": config.TEXT_COLOR,
    # "font-family": FONT_FAMILY,

}

CONTENT = {
    "display": "flex",
    "flex-wrap": "wrap",
    "justify-content": "center",
    "align-items": "center",

    "width": "100%",

    "background": config.BACKGROUND_COLOR

}

TABLE_CONTENT = {
    # "color": config.SUBTLE_TEXT_COLOR,
    "width": "100%",
    "text-align": "center",
    # "display": "flex",
    # "justify-content": "center",
    "font-size": "14px"
}