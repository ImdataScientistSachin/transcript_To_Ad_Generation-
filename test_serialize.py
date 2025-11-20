"""Quick script used during development to validate pipeline JSON serialization.

This helper runs the pipeline on a short sample and tries to JSON
serialize the full result. It is useful when debugging Streamlit UI
errors where non-serializable objects cause rendering failures.
"""
import json
from core import run_pipeline


s = b"This is a sample transcript about our new product and users love it."
res = run_pipeline(s)
print('Pipeline returned keys:', list(res.keys()))

# try to serialize — useful when debugging Streamlit rendering issues
try:
    j = json.dumps(res)
    print('JSON serialization succeeded; length:', len(j))
except Exception as e:
    print('JSON serialization failed:', type(e), e)
    # print repr of problematic values for targeted debugging
    for k, v in res.items():
        try:
            json.dumps(v)
        except Exception as e2:
            print('Key failing:', k, type(v), e2)
