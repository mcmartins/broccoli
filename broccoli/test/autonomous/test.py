import unittest
import broccoli.parser
import broccoli.job


class BroccoliTest(unittest.TestCase):
    def test(self):
        job = broccoli.parser.parse('input.json')
        self.assertIsInstance(job, broccoli.job.Job)
