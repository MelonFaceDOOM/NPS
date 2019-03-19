from tor_session import DmSession

ds = DmSession()
ds.base_url = "http://jirdqewsia3p2prz.onion/"
ds.username = "odrs"
ds.password = "odrs"
ds.login()
print(ds.get(ds.base_url).text)