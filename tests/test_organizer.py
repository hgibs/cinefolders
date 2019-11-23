import os

from cinefolders import organizer

def test_createobj():
    apikey = os.environ['TMDB_API_KEY']

    standard_options = {'copy': False,
                        'debug': True,
                        'destination': None,
                        'directory': '/tmp/videos',
                        'dry_run': False,
                        'l': False,
                        'v': False,
                        'x': None,
                        'debug': False,
                        }

    standard_options.update({'apikey':apikey})
    testo = organizer.Organizer(standard_options)
    assert True