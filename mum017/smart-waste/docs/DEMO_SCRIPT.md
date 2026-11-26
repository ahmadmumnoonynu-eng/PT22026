# 4-minute demo script

Prepare before the demo: app already running, model already downloaded (so the first prediction is quick), 4 test images ready (one high-confidence, one confusable such as paper/cardboard, one blurry or ambiguous, one not-waste or tiny image), and your evaluation numbers noted.

| Time | What to say / do |
|---|---|
| 0:00-0:30 | **Problem.** "Many people put items in the wrong bin, which contaminates recycling. My app identifies a waste item from a photo and tells you how to dispose of it." |
| 0:30-1:15 | **Model.** "It uses a pretrained Vision Transformer. The image is split into 16x16 patches, a Transformer encoder processes them with self-attention, and a classification layer outputs 12 scores. Softmax turns them into probabilities. I used a pretrained model fine-tuned on the Kaggle garbage dataset because it saves training time." |
| 1:15-2:15 | **Live demo 1.** Upload a clear image. Point out the top-3 bars, the confidence badge, the bin type, preparation steps and environmental note. |
| 2:15-3:00 | **Live demo 2 and 3.** Show a confusable item, where the warning appears. Show an ambiguous image: low confidence gives a "not sure, retake photo" message and no firm advice. Then press Classify with no image to show error handling. |
| 3:00-3:45 | **My contribution and results.** "The model is pretrained; my work is the validation, the confidence-tier logic, the recommendation engine and my own evaluation: accuracy X% on N images I collected, with most errors between ..." (use your real numbers). |
| 3:45-4:00 | **Limitations and future work.** Only 12 classes, clean-background training data, local rules vary. Future work: fine-tune on messy real photos, add a location-specific rule set. |

## Questions to prepare for

- **What is a Vision Transformer?** It splits the image into patches, treats them like words in a sentence, and uses self-attention to relate them.
- **Why softmax?** It turns raw scores into probabilities that sum to 1.
- **What does confidence mean?** It is the model's probability for the top class. It is not a guarantee, and models can be confidently wrong.
- **Why did you not train a model?** Limited time; a pretrained model gives strong features, and my focus was the application and evaluation.
- **What are the limits of the 98% figure?** It comes from the model card without a described test set, so I measured it myself.
- **Why are the thresholds 0.8 and 0.5?** They are design choices, not learned values. You can state that you chose them as sensible defaults and could tune them using your evaluation results.
