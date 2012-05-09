import urllib
import urllib2
import cookielib

AMAZON_AUTH_URL = 'https://www.amazon.com/gp/aws/ssop/index.html?awscbctx=&awscbid=urn%3Aaws%3Asid%3A027Y0TCSPRG5XHFYJSR2&awscredential=&awsnoclientpipeline=true&awsstrict=false&awsturknosubway=true&wa=wsignin1.0&wctx=&wreply=https%3A%2F%2Fwww.mturk.com%3A443%2Fmturk%2Fendsignin&wtrealm=urn%3Aaws%3Asid%3A027Y0TCSPRG5XHFYJSR2&awssig=yZwe4P9pATXcyDaYEFCDKycNYIM%3D'


def install_opener():
    """Install global opener with cookies support
    """
    jar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
    urllib2.install_opener(opener)
    return opener


def authenticate(email, password):
    """Authenticate using mturk worker account. This should be done after
    installation of opener with cookie support.
    """
    data = {'action': 'sign-in', 'password': password, 'email': email}
    resp = urllib2.urlopen(AMAZON_AUTH_URL, urllib.urlencode(data))
    return resp
