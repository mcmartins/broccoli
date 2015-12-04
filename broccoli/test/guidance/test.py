import unittest
import broccoli.logger
import broccoli.parser
from broccoli.job import Job


class BroccoliTest(unittest.TestCase):
    def test(self):
        json = broccoli.parser.parse('input.json')
        broccoli.logger.initialize(json, True)
        job = Job(json)
        self.assertIsInstance(job, broccoli.job.Job)
        job.start()
        
if __name__ == '__main__':
    unittest.main()