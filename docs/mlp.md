
# Model 6 – Multi-Layer Perceptron (MLP)

**Algorithm family:** Neural Network  
**Implementation:** `scripts/models/train_mlp.py`  
**Experiment results:** `results/experiments/mlp.json`

## A. Model Understanding

### A1. Why is MLP suitable for PathSnap?

PathSnap involves identifying the most likely road segment corresponding to each noisy GPS observation.

An MLP can learn nonlinear relationships between the engineered spatial, directional and contextual features. Unlike a linear classifier, it can learn complex feature interactions through multiple hidden layers.

The selected architecture uses two hidden layers with 64 and 32 neurons. This provides a relatively small neural network that can learn nonlinear patterns without requiring an excessively large architecture.

### A2. Major strengths and limitations

**Strengths**
- Learns nonlinear relationships between input features.
- Can model complex interactions between distance, heading and movement features.
- Supports probability predictions through `predict_proba`.
- StandardScaler improves numerical conditioning for neural-network training.
- Early stopping helps prevent unnecessary training.
- Achieved strong student-test performance in the experiment.

**Limitations**
- Requires feature scaling.
- Training is more computationally expensive than LightGBM in this experiment.
- Sensitive to hyperparameter choices and random initialisation.
- Does not inherently understand road-network connectivity.
- Uses a maximum training-row limit of one million, rather than the full candidate dataset.

## B. Training and Configuration

### B5. Important hyperparameters and initial values

The following configuration was used:

| Hyperparameter | Initial value |
|---|---:|
| hidden_layer_sizes | (64, 32) |
| alpha | 0.0001 |
| early_stopping | True |
| max_iter | 100 |
| random_state | 42 |
| max_train_rows | 1,000,000 |

The model was implemented as a scikit-learn pipeline:

1. StandardScaler
2. MLPClassifier

Scaling was fitted independently within each cross-validation training fold to avoid validation-data leakage.

Five-fold GroupKFold cross-validation was used, with complete trips kept together during splitting.

The training pipeline used a maximum of one million candidate rows, while evaluation was performed on the complete validation and student-testing datasets.

### B6. Loss function and optimisation objective

The MLP classifier uses the log-loss (cross-entropy) objective for binary classification.

L = -[y log(p) + (1-y) log(1-p)]

where:
- y represents the binary reference label.
- p represents the predicted probability of the candidate being the correct road segment.

The MLP uses the Adam optimiser by default in scikit-learn. The `alpha=0.0001` parameter applies L2 regularisation to help control model complexity.

Early stopping monitors validation performance and stops training when further iterations do not provide sufficient improvement.

## C. Experimental Results

### C7–C8. Student-test performance

The model was evaluated on all 10 student-testing trips.

| Metric | Result |
|---|---:|
| Observation-level Top-1 Accuracy | 0.8756 |
| Pair-level Macro F1 | 0.9324 |
| Log Loss | 0.03485 |
| Route Continuity | 0.9307 |
| Candidate Miss Rate | 0.000887 |

The model achieved approximately 87.56% observation-level Top-1 accuracy and 93.24% pair-level Macro F1.

Its log-loss of 0.03485 indicates strong probability performance on the student-testing dataset.

### Cross-validation performance

| Metric | Result |
|---|---:|
| Mean CV Macro F1 | 0.92327 |
| CV Macro F1 standard deviation | 0.01858 |
| Mean CV Top-1 Accuracy | 0.86722 |
| Mean CV Log Loss | 0.04884 |
| Mean CV Route Continuity | 0.93356 |

### Training history

The actual epoch-wise training history was extracted from the fitted MLP model.

The following files contain the recorded values and visualisation:

- `results/curves/mlp_history.csv`
- `results/curves/mlp_training_history.png`

The history records training loss and validation score for the fitted final MLP model.

### C9. Overfitting or underfitting analysis

The final model's training pair Macro F1 was 0.9429, while its mean cross-validation Macro F1 was 0.9233.

The difference is approximately 0.0196.

This indicates a modest training-to-validation performance gap. However, the student-test Macro F1 of 0.9324 is higher than the mean cross-validation score.

The results do not indicate severe overfitting or underfitting. The training history and early-stopping mechanism provide additional evidence for evaluating convergence and generalisation.

## Conclusion

The MLP achieved a cross-validation Macro F1 of 0.9233 and student-test Macro F1 of 0.9324.

Compared with LightGBM, MLP achieved:
- Slightly higher student-test Macro F1.
- Higher student-test Top-1 Accuracy.
- Lower student-test Log Loss.
- Higher student-test Route Continuity.
- Lower recorded inference time per observation.

However, LightGBM achieved a higher cross-validation Macro F1 and a lower cross-validation standard deviation.

MLP therefore provides a competitive neural-network baseline for PathSnap, although the final model selection should consider the complete six-model comparison and the performance of the HMM/Viterbi pipeline.

Note: Reference labels are derived by aligning GPS observations to the supplied route. They should not be treated as independently verified ground truth.
