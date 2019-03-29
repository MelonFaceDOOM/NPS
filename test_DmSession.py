import unittest
from tor_session import DmSession

class TestDmSession(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_dm_session(self):
        ds = DmSession()
        print(ds.ip)
        self.assertEqual(ds.get("http://google.com").status_code, 200)
        print("successfully reached google.com")
        self.assertEqual(ds.get("http://cannazonceujdye3.onion/").status_code, 200)
        print("successfully reached cannazon dark web market")
        ds.login()
        print("successfully logged in")
        #ds.dm_get()

if __name__ == "__main__":
    unittest.main()
