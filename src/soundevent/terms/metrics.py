from soundevent.data import Term

__all__ = [
    "accuracy",
    "average_precision",
    "balanced_accuracy",
    "f1_score",
    "jaccard_index",
    "mean_average_precision",
    "top_3_accuracy",
    "true_class_probability",
]

balanced_accuracy = Term(
    name="soundevent_metrics:balancedAccuracy",
    label="Balanced Accuracy",
    definition="The macro-average of recall scores per class or, equivalently, raw accuracy where each sample is weighted according to the inverse prevalence of its true class. Thus for balanced datasets, the score is equal to accuracy.",
)

accuracy = Term(
    uri="http://purl.obolibrary.org/obo/STATO_0000415",
    name="stato:accuracy",
    label="Accuracy",
    definition="In the context of binary classification, accuracy is defined as the proportion of true results (both true positives and true negatives) to the total number of cases examined (the sum of true positive, true negative, false positive and false negative). It can be understood as a measure of the proximity of measurement results to the true value. Accuracy is a metric used in the context of classification tasks to evaluate the proportion of correctly predicted instances among the total instances. Key Points: Use Case: Classification performance evaluation. Metric: Measures the proportion of correct predictions. Interpretation: Higher values indicate better classification performance.",
)

top_3_accuracy = Term(
    name="soundevent_metrics:top3Accuracy",
    label="Top 3 Accuracy",
    definition="The proportion of samples where the true class is in the top 3 predicted classes.",
)

true_class_probability = Term(
    name="soundevent_metrics:trueClassProbability",
    label="True Class Probability",
    definition="The model probability assigned to the true class.",
)

average_precision = Term(
    name="soundevent_metrics:averagePrecision",
    label="Average Precision",
    definition="The average precision (AP) is a metric that quantifies the quality of a binary detection task. The AP is defined as the area under the precision-recall curve.",
)

mean_average_precision = Term(
    name="soundevent_metrics:meanAveragePrecision",
    label="Mean Average Precision",
    definition="The mean of the average precision scores per class.",
    description="The average precision (AP) is a metric that quantifies the quality of a binary detection task. The AP is defined as the area under the precision-recall curve. The mean average precision (mAP) is the mean of the average precision scores per class.",
)

jaccard_index = Term(
    name="soundevent_metrics:jaccard",
    label="Jaccard Index",
    definition="The Jaccard index, also known as the Jaccard similarity coefficient, is a statistic used for comparing the similarity and diversity of sample sets. The Jaccard index is defined as the size of the intersection divided by the size of the union of two sample sets.",
)

f1_score = Term(
    name="soundevent_metrics:f1_score",
    label="F1 Score",
    definition="The F1 score is the harmonic mean of precision and recall. It is a measure of a test's accuracy that considers both the precision and recall of the test to compute the score. The F1 score is the weighted average of the precision and recall, where an F1 score reaches its best value at 1 and worst at 0.",
)
