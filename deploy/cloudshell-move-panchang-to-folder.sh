#!/bin/bash
# Copy national + demo-state regional JSONs from bucket root into panchang/ folder.
# Demo: raju/ramesh=MP, suresh=RJ, kanta=GJ, lakshmi=TS (ap_ts).
# Run in AWS Cloud Shell. Bucket: ai-sahayak-calendar

BUCKET="ai-sahayak-calendar"

# Copy national + the 4 regional files needed for demo users into panchang/
aws s3 cp "s3://${BUCKET}/national.json"           "s3://${BUCKET}/panchang/national.json"
aws s3 cp "s3://${BUCKET}/regional_mp.json"        "s3://${BUCKET}/panchang/regional_mp.json"
aws s3 cp "s3://${BUCKET}/regional_rj.json"        "s3://${BUCKET}/panchang/regional_rj.json"
aws s3 cp "s3://${BUCKET}/regional_gj.json"        "s3://${BUCKET}/panchang/regional_gj.json"
aws s3 cp "s3://${BUCKET}/regional_ap_ts.json"     "s3://${BUCKET}/panchang/regional_ap_ts.json"

echo "Done. Listing panchang/ folder:"
aws s3 ls "s3://${BUCKET}/panchang/"
