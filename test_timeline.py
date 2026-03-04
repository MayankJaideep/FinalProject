import sys
import os

sys.path.append("/Users/mayankjaideep/Desktop/ai-driven-research-engine-main/1-Rag")
from timeline_extractor import TimelineExtractor

text = """Aug 11, 2023 Act Notification
Parliament of India (DPDP
Act, 2023 passed).
Feb 2, 2026 Writ Petition
Filed Venkatesh Nayak
(Article 32 petition).
Feb 16, 2026 First Major
Hearing 3-Judge Bench (CJI
Surya Kant presiding).
Feb 16, 2026 Order Issued
Notice issued to Govt; Stay
refused; Case referred to
Larger Bench.
Mar 23, 2026 Next Hearing
Scheduled for the Constitution
Bench."""

ext = TimelineExtractor()
events = ext.extract_chronology(text)
print("EXTRACTED EVENTS:", events)
