import unittest
import broccoli.logger
import broccoli.json_parser
import broccoli.job


class BroccoliTest(unittest.TestCase):
    def test(self):
        json = broccoli.json_parser.parse('input.json')
        broccoli.logger.initialize(json, True)
        self.assertIsInstance(job, broccoli.job.Job)
        broccoli.runner.Runner(job)

if __name__ == '__main__':
    unittest.main()