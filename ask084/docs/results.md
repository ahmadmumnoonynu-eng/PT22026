# Results on 500 random CoNLL-2003 test sentences (seed 42)

| Model | Precision | Recall | F1 |
|---|---|---|---|
| BERT (dslim/bert-base-NER) | 0.877 | 0.922 | 0.899 |
| spaCy en_core_web_sm (mapped labels) | 0.674 | 0.535 | 0.597 |

## Per-entity F1

| Model | PER | ORG | LOC | MISC |
|---|---|---|---|---|
| BERT (dslim/bert-base-NER) | 0.887 | 0.904 | 0.933 | 0.827 |
| spaCy en_core_web_sm (mapped labels) | 0.690 | 0.410 | 0.715 | 0.536 |
