import unittest

import broccoli.parser


class BroccoliTest(unittest.TestCase):

    def test_job_creation(self):
        config = broccoli.parser.parse('input.json')
        job = broccoli.job.Job(config)
        self.assertEqual(job.name, 'Job1')
        self.assertEqual(job.description, 'Job1 Description')
        self.assertIsNotNone(job.get_tasks())
        self.assertEqual(len(job.get_tasks()), 2)
        task = job.get_tasks().get(0)
        self.assertEqual(task.name, 'Task1')
        self.assertEqual(task.description, 'Task1 Description')
        self.assertIsNotNone(task.get_sub_tasks())
        self.assertIsNotNone(task.get_children())