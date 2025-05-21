#!/bin/bash
export $(cat .env | grep -v ^# | xargs)
python main.py --mode test --alpha cross_chain
