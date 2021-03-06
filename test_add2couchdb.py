import unittest
from OBSCouchDB import OBSCouchDB

class Add(unittest.TestCase):

    obsCdb = None
    test_link = "https://github.com/vrtmrz/obsidian-livesync/"
    # target_doc_id = "UndefinedDummyFailure"
    target_doc_id = "1-Obsidian/Test.md" # change this to an existing document in Obsidian

    def setUp(self):
        self.obsCdb = OBSCouchDB(self.target_doc_id)
        self.assertTrue(self.obsCdb.init_ok, self.obsCdb.error_msg)
        self.obsCdb.trace = True

    def test01_add_content(self):
        self.assertTrue(self.obsCdb!=None)
        status = self.obsCdb.add_content(self.test_link)
        print(status)
        self.assertEqual(status, f"Appended content to {self.target_doc_id}")

    def test02_get_last_child(self):
        self.assertTrue(self.obsCdb!=None)
        result = self.obsCdb.get_last_child()
        data = result['data'].strip() 
        self.assertEqual(data, self.test_link)

    # comment this test out if you want to manually check in Obsidian if the link has been added
    def test03_delete_last_child(self):
        self.assertTrue(self.obsCdb!=None)
        result = self.obsCdb.delete_last_child()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main(failfast=True)
