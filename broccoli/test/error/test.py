import unittest
import broccoli.parser
import broccoli.job


class BroccoliTest(unittest.TestCase):

    def test_parser_invalid_input(self):
        with self.assertRaises(broccoli.parser.InvalidInput):
            broccoli.parser.parse('non_existent.json')

    """def test_parser_malformed_input(self):
        with self.assertRaises(broccoli.parser.MalformedJSONInput):
            broccoli.parser.parse("{\"jobName\": \"Boolean Algebra 2-Basis\"}")
    """