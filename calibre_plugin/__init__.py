from calibre.customize import InterfaceActionBase


class KoboRatingsPlugin(InterfaceActionBase):
    name = 'Kobo Ratings'
    description = 'Copy Kobo rating shelves into the #myratings column of the open library'
    supported_platforms = ['osx']
    author = 'Jennifer Lyn Parsons'
    version = (0, 1, 0)
    minimum_calibre_version = (9, 0, 0)
    actual_plugin = 'calibre_plugins.kobo_ratings.action:KoboRatingsAction'
