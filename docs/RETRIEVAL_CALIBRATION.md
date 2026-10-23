# Retrieval calibration

Threshold: 0.596218667000. Score: 1 / (1 + Chroma L2 distance).

Selected the highest threshold retaining every verified positive. No generation calls were used for calibration.
Positive source-page retrieval: 7/7. Negative generation bypasses: 13/18.

A retrieval score is not proof that the document answers a question. Five negatives remain above the threshold and require grounded generation/verification. Final QA negative accuracy is not yet measured.

| Question | Answerable | Score | Retrieved pages |
|---|---|---:|---|
| On what date were the prices in this catalogue last updated? | True | 0.670034 | 2, 3, 10, 24, 32, 36, 48, 50, 54, 57, 85, 91 |
| In which year was the publisher (Orient BlackSwan) incorporated? | True | 0.687444 | 2, 3, 19, 20, 57, 71, 83, 85 |
| What is the price of a Physics textbook? | False | 0.613503 | 8, 46, 54, 56, 63, 70, 81, 85, 91 |
| Who is the current Minister of Education? | False | 0.568498 | 7, 9, 11, 34, 37, 38, 42, 91 |
| Which is the "best" history book for a beginner? | False | 0.609153 | 2, 9, 10, 16, 26, 49, 50, 56, 57, 61, 62 |
| Which email address handles rights-related queries? | True | 0.605694 | 3, 15, 22, 25, 33, 64, 72, 82, 89 |
| Which email address accepts book orders? | True | 0.624057 | 3, 11, 13, 14, 32, 54, 68, 73 |
| Where can I submit an online book proposal? | True | 0.622136 | 3, 36, 65, 68, 69, 79, 80 |
| On what printed page does the Author Index begin? | True | 0.610959 | 3, 5, 15, 83, 84 |
| On what printed page does the Title Index begin? | True | 0.596220 | 3, 48, 86, 87, 88, 89, 90 |
| What is the current GST rate in India? | False | 0.562762 | 2, 5, 6, 10, 12, 14, 54, 70, 87, 88, 91 |
| What is the capital of France? | False | 0.559514 | 7, 19, 20, 32, 39, 48, 57, 59, 91 |
| Who is the current Prime Minister of India? | False | 0.577394 | 5, 7, 9, 33, 37, 65, 68, 71 |
| Give me a cooking recipe for pasta. | False | 0.555464 | 3, 12, 14, 24, 27, 28, 32, 39, 48, 57, 91 |
| What is the price of a Chemistry textbook? | False | 0.603847 | 8, 36, 48, 56, 63, 85, 88, 91 |
| What is the price of a Biology textbook? | False | 0.609487 | 8, 28, 56, 63, 73, 85, 88, 91 |
| What is the price of a Mathematics textbook? | False | 0.623354 | 8, 46, 56, 63, 87, 88, 89, 91 |
| What is the weather in Delhi today? | False | 0.563653 | 4, 6, 12, 13, 20, 23, 29, 55, 64, 75, 82 |
| What is the current Bitcoin price? | False | 0.591345 | 15, 32, 36, 39, 48, 57, 85, 91 |
| What is the WiFi password? | False | 0.550263 | 3, 5, 32, 59, 86, 89, 91 |
| How do I reset my bank password? | False | 0.526565 | 3, 5, 32, 41, 46, 48, 54, 68, 91 |
| What is the melting point of titanium? | False | 0.543778 | 9, 15, 20, 32, 36, 37, 41, 48, 57, 62, 91 |
| What are the results of today’s cricket match? | False | 0.561335 | 13, 22, 28, 29, 32, 54, 74, 91 |
| Who won the 2026 Nobel Prize in Physics? | False | 0.590660 | 10, 13, 22, 32, 36, 48, 50, 54, 57, 60, 85, 91 |
| What is the newest iPhone price? | False | 0.584632 | 3, 13, 32, 36, 48, 54, 57, 85, 91 |
