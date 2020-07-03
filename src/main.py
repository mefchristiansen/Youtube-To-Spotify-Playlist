""" Lambda Handler

AWS Lambda will invoke the handler function defined below when it executes.

"""

import youtube_to_spotify

def handler(event, context):
	youtube_to_spotify.main()