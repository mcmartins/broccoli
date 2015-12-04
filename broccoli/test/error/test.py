import unittest
import broccoli.json_parser
import broccoli.job


class BroccoliTest(unittest.TestCase):

    def test_parser_invalid_input(self):
        with self.assertRaises(broccoli.json_parser.InvalidInput):
            broccoli.json_parser.parse('non_existent.json')

    def test_parser_malformed_input(self):
        with self.assertRaises(broccoli.json_parser.MalformedJSONInput):
            broccoli.json_parser.parse("{\"jobName\": \"Boolean Algebra 2-Basis\"}")
    
if __name__ == '__main__':
    unittest.main()