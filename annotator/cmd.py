import argparse
import os
import logging
import traceback

from tadae.settings import LOG_DIR
from workflow import dotype, annotate_csv

from tadae.models import AnnRun

from commons.logger import set_config

logger = set_config(logging.getLogger(__name__), logdir=os.path.join(LOG_DIR, 'tadae.log'))

if __name__ == '__main__':
    global logger
    endpoint = "http://dbpedia.org/sparql"
    parser = argparse.ArgumentParser(description='Annotation module to annotate a given annotation run')
    parser.add_argument('runid', type=int, metavar='Annotation_Run_ID', help='the id of the Annotation Run ')
    parser.add_argument('--csvfiles', action='append', nargs='+', help='the list of csv files to be annotated')
    parser.add_argument('--dotype', action='store_true', help='To conclude the type/class of the given csv file')
    parser.add_argument('--camelcase', action='store_true', help='To make each cell in the subject column into camelcase')
    parser.add_argument('--onlyprefix', action='store', help='To limit to classes that starts with this prefix')
    parser.add_argument('--entitycol', type=int, action='store', help='The id of the entity column in the csv file')
    parser.add_argument('--logdir', action='store', help='suffix to the log file')
    args = parser.parse_args()
    if args.logdir:
        logger = set_config(logging.getLogger(__name__), logdir=args.logdir)
    if args.csvfiles and len(args.csvfiles) > 0:
        logger.debug('csvfiles: %s' % args.csvfiles)
        logger.debug("adding dataset")
        logger.debug("csv_file_dir: ")
        logger.debug(args.csvfiles[0])
        camel_case = False
        if args.camelcase:
            camel_case = True
        prefix = None
        if args.onlyprefix:
            prefix = args.onlyprefix
        try:
            annotate_csv(ann_run_id=args.runid, hierarchy=False, csv_file_dir=args.csvfiles[0][0], camel_case=camel_case,
                         endpoint="http://dbpedia.org/sparql", entity_col_id=args.entitycol, onlyprefix=prefix)
            logger.info("data set is added successfully.")
        except Exception as e:
            logger.error("exception: ")
            logger.error(str(e))
            err_msg = traceback.extract_stack
            logger.error(err_msg)

    if args.dotype:
        prefix = None
        # The hierarchy is not restricted to the passed prefix
        # if args.onlyprefix:
        #     prefix = args.onlyprefix
        ann_run = AnnRun.objects.get(id=args.runid)
        logger.debug('typing the csv file')
        try:
            dotype(ann_run=ann_run, endpoint=endpoint, onlyprefix=prefix)
            logger.info('done typing the csv file')
        except Exception as e:
            logger.error("exception: ")
            logger.error(str(e))
            err_msg = traceback.extract_stack
            logger.error(err_msg)