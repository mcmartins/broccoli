import logging


def main(job_name):
    logging.basicConfig(format='[%(levelname)s] - %(asctime)s: %(message)s',
                        filename='Broccoli-Job-' + job_name + '.log', level=logging.DEBUG)
    logging.info('Started')
