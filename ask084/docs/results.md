# Results on 3453 random CoNLL-2003 test sentences (seed 42)

| Model | Precision | Recall | F1 |
|---|---|---|---|
| BERT (dslim/bert-base-NER) | 0.864 | 0.915 | 0.888 |
| spaCy en_core_web_sm (mapped labels) | 0.656 | 0.545 | 0.595 |

## Per-entity F1

| Model | PER | ORG | LOC | MISC |
|---|---|---|---|---|
| BERT (dslim/bert-base-NER) | 0.887 | 0.891 | 0.926 | 0.799 |
| spaCy en_core_web_sm (mapped labels) | 0.646 | 0.360 | 0.749 | 0.614 |
