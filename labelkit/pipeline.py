import json
from typing import List, Callable, Union, Dict
from collections import defaultdict
from dataclasses import dataclass, field
import pandas as pd
from .steps import Step, LLMStep


@dataclass
class PipelineStatistics:
    input_tokens: dict = field(default_factory=lambda: defaultdict(int))
    output_tokens: dict = field(default_factory=lambda: defaultdict(int))
    input_cost: dict = field(default_factory=lambda: defaultdict(float))
    output_cost: dict = field(default_factory=lambda: defaultdict(float))
    num_success: int = 0
    num_failure: int = 0
    total_latency: float = 0.0

    def __str__(self):
        return json.dumps({
            "input_tokens": dict(self.input_tokens),
            "output_tokens": dict(self.output_tokens),
            "input_cost": dict(self.input_cost),
            "output_cost": dict(self.output_cost),
            "num_success": int(self.num_success),
            "num_failure": int(self.num_failure),
            "total_latency": float(self.total_latency)
        }, indent=4)


class Pipeline:
    """
    A class representing a pipeline of steps to process data.

    Attributes:
        steps (List[Step]): A list of steps (processing units) in the pipeline.
        evaluation_fn (Callable[[any], bool], optional): An optional function to evaluate the processed data.
        data (Union[pd.DataFrame, Dict], optional): The data processed by the pipeline. Initially None.
        score (float, optional): The evaluation score of the processed data. Initially None.
        statistics (PipelineStatistics): Statistics of the pipeline's execution.

    Methods:
        apply(data): Applies the pipeline steps to the input data.
        update_params(params): Updates the parameters of the pipeline steps.
        evaluate(evaluation_fn=None): Evaluates the processed data using an evaluation function.
        _aggregate_statistics(data): Aggregates statistics from the pipeline steps.
    """

    def __init__(self,
                 steps: List[Step],
                 evaluation_fn: Callable[[any], bool] = None):
        self.steps = steps
        self.evaluation_fn = evaluation_fn
        self.data = None
        self.score = None
        self.statistics = PipelineStatistics()

    def apply(self, data: Union[pd.DataFrame, Dict], verbose=True):
        for step in self.steps:
            step.apply(data, verbose)
        self._aggregate_statistics(data)
        if isinstance(data, pd.DataFrame):
            self.data = data
            if self.evaluation_fn is not None:
                self.evaluate()
        return data

    def update_params(self, params: Dict):
        for step in self.steps:
            global_params = params.get('global', {})
            step_params = params.get(step.name, {})
            step.update_params({**global_params, **step_params})

    def evaluate(self, evaluation_fn=None):
        evaluation_fn = evaluation_fn or self.evaluation_fn
        if evaluation_fn is None:
            print("No evaluation function provided")
            return
        elif self.data is None:
            print("No data provided")
            return
        results = self.data.apply(lambda row: evaluation_fn(row), axis=1)
        self.score = results.sum() / len(results)
        return self.score

    def _aggregate_statistics(self, data: Union[pd.DataFrame, Dict]):
        self.statistics = PipelineStatistics()
        if isinstance(data, pd.DataFrame):
            success = data.apply(lambda x: True, axis=1)
        else:
            success = True
        for step in self.steps:
            if isinstance(step, LLMStep):
                model = step.model
                self.statistics.input_tokens[model] += step.statistics.input_tokens
                self.statistics.output_tokens[model] += step.statistics.output_tokens
                self.statistics.input_cost[model] += step.statistics.input_cost
                self.statistics.output_cost[model] += step.statistics.output_cost
                self.statistics.total_latency += step.statistics.total_latency

                if isinstance(data, pd.DataFrame):
                    success = success & data.apply(
                        lambda x: x[f"__{step.name}__"]["success"], axis=1)
                    self.statistics.num_success = success.sum()
                    self.statistics.num_failure = len(
                        data) - self.statistics.num_success
                else:
                    success = success & data[f"__{step.name}__"]["success"]
                    self.statistics.num_success = 1 if success else 0
