"""Rebuild from the frozen snapshot. --ingest collects missing raw files first."""
import argparse
import subprocess
import sys
from common import ROOT


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--ingest',action='store_true')
    parser.add_argument('--with-story',action='store_true',help='Requires requirements-dev.txt; creates PDFs too.')
    args=parser.parse_args()
    stages=(['ingest_data'] if args.ingest else [])+['clean_data','validate_data','model_data','build_basket','analyze_prices','make_visuals','build_site']
    if args.with_story:stages+=['write_reports','make_storytelling']
    for stage in stages:
        print(f'\nRunning {stage}',flush=True)
        subprocess.run([sys.executable,str(ROOT/'src'/f'{stage}.py')],cwd=ROOT,check=True)


if __name__=='__main__':main()
