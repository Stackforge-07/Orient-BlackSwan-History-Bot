"""Verified evaluation cases; QA does not import these answers."""
ASSIGNMENT = [
 ('On what date were the prices in this catalogue last updated?', '20-01-2025', 2),
 ('In which year was the publisher (Orient BlackSwan) incorporated?', '1948', 2),
 ('What is the price of a Physics textbook?', 'Not found', None),
 ('Who is the current Minister of Education?', 'Not found', None),
 ('Which is the "best" history book for a beginner?', 'Not found', None),
]
NEGATIVES = ['What is the current GST rate in India?', 'What is the capital of France?',
 'Who is the current Prime Minister of India?', 'Give me a cooking recipe for pasta.',
 'What is the price of a Chemistry textbook?', 'What is the price of a Biology textbook?',
 'What is the price of a Mathematics textbook?', 'What is the weather in Delhi today?',
 'What is the current Bitcoin price?', 'What is the WiFi password?',
 'How do I reset my bank password?', 'What is the melting point of titanium?',
 'What are the results of today’s cricket match?', 'Who won the 2026 Nobel Prize in Physics?',
 'What is the newest iPhone price?']
EXTRA = [
 ('Which email address handles rights-related queries?', 'rights@orientblackswan.com', 3),
 ('Which email address accepts book orders?', 'info@orientblackswan.com', 3),
 ('Where can I submit an online book proposal?', 'www.orientblackswan.com/publish', 3),
 ('On what printed page does the Author Index begin?', '80', 3),
 ('On what printed page does the Title Index begin?', '83', 3),
]
