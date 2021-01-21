import dash
import os
import dash_bootstrap_components as dbc
import dash_html_components as html


KIWI_LOGO = "../static/logo2.png"

# hypelinks
kiwibot = "https://www.kiwibot.com/"


def navbar():
    navbar = dbc.Navbar(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=KIWI_LOGO, height="20px"))
                        # dbc.Col(dbc.NavbarBrand("Navbar", className="ml-2")),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href=kiwibot,
                dbc.Row(< div class="collapse navbar-collapse" id="navbarColor02" >
                         < ul class="navbar-nav mr-auto" >
                         < li class="nav-item active" >
                         < a class="nav-link" href="#" > Home
                         < span class="sr-only" > (current) < /span >
                         < / a > )
            ], sticky="top",
            color="#000000",
            dark=True))

    """),dbc.Row(children=[dbc.NavItem(dbc.NavLink("Analytics", href="/analytics")),
                             dbc.NavItem(dbc.NavLink(
                                 "Clusterization", href="/clusters")),
                             dbc.NavItem(dbc.NavLink(
                                 "About Us", href="/about", className='nav-item'))
                             ]
                   ), ],
)"""

    """navbar = dbc.NavbarSimple(
        children=[
            dbc.Button([html.Img(src=KIWI_LOGO, height="25px")],
                       active=True, color="FFFFFF", align='left',
                       href=kiwibot, className="ml-2"),
            dbc.NavItem(dbc.NavLink("Analytics", href="/analytics")),
            dbc.NavItem(dbc.NavLink("Clusterization", href="/clusters")),
            dbc.NavItem(dbc.NavLink("About Us", href="/about")),
        ],
        # brand=KIWI_LOGO,
        sticky="top",
        color="#000000",
        dark=True,
    )"""
    return navbar
