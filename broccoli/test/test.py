import unittest

import broccoli.parser


class BroccoliTest(unittest.TestCase):

    def test_parser(self):
        config = broccoli.parser.parse('input.json')
        job = broccoli.job.Job(config)
        tasks = job.pop_tasks()
        task = tasks.pop(0)
        commands = task.get_commands
        guidance_tasks = task.pop_guidance()
        guidance_task = guidance_tasks.pop(0)
        guidance_commands = guidance_task.get_commands
