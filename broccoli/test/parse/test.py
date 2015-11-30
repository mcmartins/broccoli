import unittest

import broccoli.parser


class BroccoliTest(unittest.TestCase):

    def test_parser(self):
        config = broccoli.parser.parse('input.json')
        job = broccoli.job.Job(config)
        self.assertEqual(job.name, 'Job1')
        self.assertEqual(job.description, 'Job1 Description')