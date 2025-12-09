# ReDial Reproducibility Study

This repository contains a reproducibility study of conversational recommendation methods on the ReDial dataset.

## Overview

We investigate and reproduce results from multiple state-of-the-art conversational recommender systems that have been evaluated on the ReDial dataset. This study analyzes the different preprocessing approaches, evaluation protocols, and methodological choices across these methods.

## Methods

| Method | KG | Metadata | NN | Seq2Seq | Train | Test |
|--------|----|---------|----|---------|-------|------|
| KBRD (Chen et al., 2019) | ✓ | ✗ | ✓ | ✗ | 26,487 | 3,477 |
| KGSF (Zhou et al., 2020) | ✓ | ✗ | ✓ | ✗ | 26,487 | 3,477 |
| UniCRS (Wang et al., 2022) | ✓ | ✗ | ✗ | ✓ | 26,487 | 3,477 |
| ECR (Zhang et al., 2024) | ✓ | ✗ | ✗ | ✓ | 34,148 | 4,200 |
| MESE (Yang et al., 2022) | ✗ | ✓ | ✓ | ✗ | 71,961 | 9,237 |
| PECRS (Ravaut et al., 2024) | ✗ | ✓ | ✓ | ✗ | 71,961 | 9,237 |
| ReFICR (Yang et al., 2024) | ✗ | ✓ | ✓ | ✗ | - | - |

**Metadata columns:**
- **KG**: Uses knowledge graph
- **Metadata**: Uses movie metadata (e.g., plots, genres)
- **NN**: Neural network-based recommendation
- **Seq2Seq**: Sequence-to-sequence generation approach
- **Train/Test**: Number of recommendation instances

## Dataset Preprocessing Differences

Different methods use varying preprocessing strategies for the ReDial dataset:

### CRSLab-based Methods (KBRD, KGSF, UniCRS)
- **Instances**: 26,487 train / 3,477 test
- Process recommender utterances only
- Create one instance per movie mention
- Train+Valid combined: 9,005 conversations

### ECR
- **Instances**: 34,148 train / 4,200 test
- Process recommender utterances only
- Includes both movie IDs and entity IDs
- Evaluates on recommender utterances only (as per paper)

### PECRS/MESE
- **Instances**: 71,961 train / 9,237 test
- Process recommender utterances only
- **Splits utterances with multiple recommendations into separate instances** (one per movie)
- Includes instances without recommendations (target = -1)
- Significantly more instances due to splitting approach

### Our Preprocessing (Deduplicated)
- **Instances**: 31,875 train / 3,838 test
- Process recommender utterances only
- Filters out movies already mentioned earlier in conversation
- One instance per recommender utterance (not per movie)

## Repository Structure

```
data/
  dataset_statistics.txt           # Our preprocessing statistics
  crslab_dataset_statistics.txt    # CRSLab methods statistics
  ecr_dataset_statistics.txt       # ECR statistics
  efficient_unified_crs_dataset_statistics.txt  # PECRS statistics
scripts/
  create_recommendation_dataset.py # Dataset preprocessing script
```

## References

- Chen et al. (2019). "Towards Knowledge-Based Recommender Dialog System." EMNLP.
- Zhou et al. (2020). "Improving Conversational Recommender Systems via Knowledge Graph based Semantic Fusion." KDD.
- Wang et al. (2022). "Towards Unified Conversational Recommender Systems via Knowledge-Enhanced Prompt Learning." KDD.
- Yang et al. (2022). "Improving Conversational Recommendation Systems via Counterfactual Data Simulation." NAACL.
- Zhang et al. (2024). "Towards Empathetic Conversational Recommender Systems." RecSys.
- Ravaut et al. (2024). "On the Role of Knowledge Graph Construction in Conversational Recommender Systems." EACL.
- Yang et al. (2024). "Large Language Model Can Interpret Latent Space of Sequential Recommender." RecSys.
