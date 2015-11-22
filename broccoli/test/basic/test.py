import unittest
import broccoli.logger
import broccoli.parser
import broccoli.runner
import broccoli.job


class BroccoliTest(unittest.TestCase):
    def test(self):
        job = broccoli.parser.parse('input.json')
        self.assertIsInstance(job, broccoli.job.Job)
        broccoli.logger.initialize(job, True)
        broccoli.runner.Runner(job)
