import unittest
import broccoli.parser
import broccoli.job


class BroccoliTest(unittest.TestCase):
    def testParser(self):
        job = broccoli.parser.parse('test.json')
        self.assertIsInstance(job, broccoli.job.Job)

    def testParserInvalidInput(self):
        with self.assertRaises(broccoli.parser.InvalidInput):
            broccoli.parser.parse('non_existent.json')

    """def testParserMalformedInput(self):
        with self.assertRaises(broccoli.parser.MalformedJSONInput):
            broccoli.parser.parse("{\"jobName\": \"Boolean Algebra 2-Basis\"}")
    """
