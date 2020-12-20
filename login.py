import os
from flask import Flask, request


from Authentication import SteamSignIn

app = Flask(__name__)

@app.route('/')
def main():

	shouldLogin = request.args.get('login')
	if shouldLogin is not None:
		steamLogin = SteamSignIn()
		# Flask expects an explicit return on the route.
		return steamLogin.RedirectUser(steamLogin.ConstructURL('http://localhost:8080/processlogin'))

	return 'Click <a href="/?login=true">to log in</a>'

@app.route('/processlogin')
def process():

	returnData = request.values

	steamLogin = SteamSignIn()
	steamID = steamLogin.ValidateResults(returnData)

	print('SteamID returned is: ', steamID)

	if steamID is not False:
		return 'We logged in successfully!<br />SteamID: {0}'.format(steamID)
	else:
		return 'Failed to log in, bad details?'


if __name__ == '__main__':
	os.environ['FLASK_ENV'] = 'development'
	app.run(host = 'localhost', port = 8080, debug = False)