import argparse
from models.records import Record,Score

parser = argparse.ArgumentParser(description="Path to exported maitools JSON.")
parser.add_argument("songs_json", type=str, help="Path to songs JSON.")
parser.add_argument("scores_json", type=str, help="Path to exported maitools JSON.")

args = parser.parse_args()
    
    
print("JSON path provided:", args.json_path)

