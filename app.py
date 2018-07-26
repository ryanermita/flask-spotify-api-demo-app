from flask import Flask, request, redirect, jsonify
import requests
from urllib.parse import urlencode

app = Flask(__name__)

CLIENT_ID = "<CLIENT ID>"
CLIENT_SECRET = "<CLIENT SECRET>"
REDIRECT_URI = "http://localhost:5000/auth/callback"
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1"

# visit here for more scopes:
# https://developer.spotify.com/documentation/general/guides/scopes/
SCOPES = "user-read-private user-read-email playlist-read-private playlist-modify-public playlist-modify-private playlist-read-collaborative"

# use tuple to have urlencode encode
# the items in order,
# client_id must comes first else spotify will raise missing client_id
auth_query_parameters = [
    ("client_id", CLIENT_ID),
    ("response_type", "code"),
    ("redirect_uri", REDIRECT_URI),
    ("scope", SCOPES),
]


@app.route("/")
def index():
    spotify_auth_url_query_strings = urlencode(auth_query_parameters)
    spotify_auth_url = "{auth_url}/?{query_strings}".format(auth_url=SPOTIFY_AUTH_URL,
                                                            query_strings=spotify_auth_url_query_strings)

    return redirect(spotify_auth_url)


@app.route("/auth/callback")
def spotify_auth_callback():

    # TODO:
    # Use header approach to get access token.
    # currently we're using the payload approach to get the acces_token
    # because when using the header approach spofify raises invalid_client
    # already filed an issue regarding this.
    # https://github.com/spotify/web-api/issues/964

    auth_token = request.args['code']

    request_token_payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": auth_token,
        "redirect_uri": REDIRECT_URI
    }

    request_auth_token = requests.post(SPOTIFY_TOKEN_URL, data=request_token_payload)

    if request_auth_token.status_code != 200:
        return jsonify(request_auth_token.json()), request_auth_token.status_code

    access_token = request_auth_token.json().get("access_token")
    headers = {"Authorization": "Bearer {}".format(access_token)}

    # Fetch user profile
    spotify_user_url = "{}/me".format(SPOTIFY_API_URL)
    request_spofify_user = requests.get(spotify_user_url, headers=headers)

    # Fetch user's playlist
    user_id = request_spofify_user.json().get("id")
    spotify_user_playlist_url = "{}/users/{}/playlists".format(SPOTIFY_API_URL, user_id)
    request_spofify_user_playlist = requests.get(spotify_user_playlist_url, headers=headers)

    response = {"user_details": request_spofify_user.json(),
                "user_playlist": request_spofify_user_playlist.json()}

    return jsonify(response), request_spofify_user.status_code


if __name__ == "__main__":
    app.run(debug=True)
