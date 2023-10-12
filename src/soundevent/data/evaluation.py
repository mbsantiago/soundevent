"""Evaluation Model Module.

The `Evaluation` class within the `soundevent.data` package encapsulates the
core components of a bioacoustic evaluation process. This model is central to
assessing the performance of machine learning models in bioacoustic tasks. The
evaluation comprises an `EvaluationSet`, a specific `ModelRun`, computed
metrics, and a set of `EvaluatedExample` instances.
"""
from typing import Optional, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator

from soundevent.data.evaluated_example import EvaluatedExample
from soundevent.data.evaluation_set import EvaluationSet
from soundevent.data.features import Feature
from soundevent.data.model_run import ModelRun


class Evaluation(BaseModel):
    """Evaluation Model Class.

    The `Evaluation` class represents a comprehensive evaluation of a machine
    learning model's performance in bioacoustic tasks. It encapsulates crucial
    components of the evaluation process, including the evaluation set, model
    run details, computed metrics, and individual evaluated examples.

    Attributes
    ----------
    evaluation_set
        An instance of the `EvaluationSet` class representing the curated set of
        annotated clips used for model evaluation. This evaluation set serves as
        the ground truth against which the model's predictions are compared,
        enabling a rigorous assessment of the model's performance.
    model_run
        An instance of the `ModelRun` class representing the specific run of the
        machine learning model being evaluated. This encapsulates the model's
        configuration, architecture, and parameters, facilitating reproducibility
        and detailed analysis of the evaluation results. Understanding the model
        run details is crucial for interpreting the evaluation outcomes effectively.
    metrics
        A list of `Feature` instances representing computed metrics derived from the
        model's predictions and the ground truth annotations. These metrics provide
        quantitative insights into the model's performance, including accuracy,
        precision, recall, and other relevant evaluation criteria. Analyzing these
        metrics enables researchers to identify the strengths and weaknesses of the
        model's predictions.
    evaluated_examples
        A list of `EvaluatedExample` instances representing individual clips that
        have been evaluated by the model. Each `EvaluatedExample` contains the
        audio clip, its annotations, the model's predictions, and relevant evaluation
        scores. These examples allow for detailed analysis of the model's behavior
        on specific instances, facilitating targeted improvements and optimizations.
    score
        A single floating-point value representing the overall performance of the
        model on the evaluation set.
    """

    evaluation_set: EvaluationSet
    model_run: ModelRun
    metrics: Sequence[Feature] = Field(default_factory=list)
    evaluated_examples: Sequence[EvaluatedExample] = Field(
        default_factory=list
    )
    score: Optional[float] = Field(default=None, alias="score")

    model_config = ConfigDict(protected_namespaces=())

    @model_validator(mode="after")  # type: ignore
    def _check_evaluated_samples_belong_to_set(self):
        """Check that all evaluated examples belong to the evaluation set."""
        evaluation_set_examples = {
            example.uuid for example in self.evaluation_set.examples
        }
        if any(
            evaluated.example.uuid not in evaluation_set_examples
            for evaluated in self.evaluated_examples
        ):
            raise ValueError(
                "Not all evaluated examples belong to the evaluation set."
            )
        return self
