"""Harbor integration for parallel benchmark execution.

This module provides integration with Harbor for running benchmarks
with parallel execution. Harbor is a distributed benchmark execution
framework that provides dataset loading and agent interfaces.

If Harbor is not available, this module falls back to local execution.
"""

import asyncio
import os
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar

from src.evaluation.evaluate import EvalResult

T = TypeVar("T")


class HarborDataset(ABC, Generic[T]):
    """Abstract base class for Harbor datasets."""

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of items in the dataset."""
        pass

    @abstractmethod
    def __getitem__(self, index: int) -> T:
        """Get item at index."""
        pass


class HarborAgent(ABC):
    """Abstract base class for Harbor agents."""

    @abstractmethod
    async def run(self, input_data: Any) -> Any:
        """Run the agent on input data."""
        pass


def is_harbor_available() -> bool:
    """Check if Harbor is available in the environment."""
    return os.environ.get("HARBOR_ENABLED", "").lower() == "true"


async def run_via_harbor(
    dataset: list[Any],
    agent_factory: Callable[[], Any],
    max_concurrent: int = 4,
    output_path: str | None = None,
) -> list[EvalResult]:
    """Run evaluation via Harbor if available, otherwise use local execution.

    Args:
        dataset: List of items to evaluate
        agent_factory: Factory function that creates a new agent instance
        max_concurrent: Maximum concurrent evaluations
        output_path: Optional path to save results

    Returns:
        List of evaluation results
    """
    if not is_harbor_available():
        # Fall back to local execution
        return await run_local(dataset, agent_factory, max_concurrent, output_path)

    # Harbor execution path
    # Note: This requires Harbor to be properly configured
    try:
        return await run_harbor_parallel(
            dataset, agent_factory, max_concurrent, output_path
        )
    except ImportError:
        # Harbor not installed, fall back to local
        return await run_local(dataset, agent_factory, max_concurrent, output_path)


async def run_local(
    dataset: list[Any],
    agent_factory: Callable[[], Any],
    max_concurrent: int = 4,
    output_path: str | None = None,
) -> list[EvalResult]:
    """Run evaluation locally (fallback when Harbor is not available).

    Args:
        dataset: List of items to evaluate
        agent_factory: Factory function that creates a new agent instance
        max_concurrent: Maximum concurrent evaluations
        output_path: Optional path to save results

    Returns:
        List of evaluation results
    """
    from src.evaluation.eval_full import evaluate_full

    # Create agent
    from src.schemas import AgentResponse

    agent = agent_factory()

    # Use the existing evaluate_full function
    items = [(i, item, None) for i, item in enumerate(dataset)]

    results = []
    semaphore = asyncio.Semaphore(max_concurrent)

    async def eval_item(item):
        async with semaphore:
            idx, data, _ = item
            trace = await agent.run(data)
            return EvalResult(
                index=idx,
                question=data,
                ground_truth=None,
                trace=trace,
                error=trace.parse_error if trace.is_error else None,
            )

    # Run evaluations
    tasks = [eval_item(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out exceptions and convert to EvalResult
    evaluation_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            evaluation_results.append(
                EvalResult(
                    index=i,
                    question=dataset[i],
                    ground_truth=None,
                    trace=None,
                    error=str(result),
                )
            )
        else:
            evaluation_results.append(result)

    return evaluation_results


async def run_harbor_parallel(
    dataset: list[Any],
    agent_factory: Callable[[], Any],
    max_concurrent: int = 4,
    output_path: str | None = None,
) -> list[EvalResult]:
    """Run evaluation via Harbor's parallel execution system.

    This is a placeholder for the actual Harbor integration.
    Harbor would provide:
    - Dataset loading and sharding
    - Parallel agent execution across workers
    - Result aggregation

    Args:
        dataset: List of items to evaluate
        agent_factory: Factory function that creates a new agent instance
        max_concurrent: Maximum concurrent evaluations
        output_path: Optional path to save results

    Returns:
        List of evaluation results

    Raises:
        ImportError: If Harbor is not available
    """
    # This is where Harbor-specific code would go
    # For now, we fall back to local execution
    raise ImportError("Harbor integration not yet implemented")


class HarborRunner:
    """Runner for executing benchmarks via Harbor.

    This class provides a simplified interface for running benchmarks
    with optional Harbor integration for parallel execution.
    """

    def __init__(
        self,
        max_concurrent: int = 4,
        use_harbor: bool = False,
        output_path: str | None = None,
    ):
        """Initialize the Harbor runner.

        Args:
            max_concurrent: Maximum concurrent evaluations
            use_harbor: Whether to use Harbor (if available)
            output_path: Optional path to save results
        """
        self.max_concurrent = max_concurrent
        self.use_harbor = use_harbor and is_harbor_available()
        self.output_path = output_path

    async def run(
        self,
        dataset: list[Any],
        agent_factory: Callable[[], Any],
    ) -> list[EvalResult]:
        """Run evaluation on the dataset.

        Args:
            dataset: List of items to evaluate
            agent_factory: Factory function that creates a new agent instance

        Returns:
            List of evaluation results
        """
        if self.use_harbor:
            return await run_via_harbor(
                dataset=dataset,
                agent_factory=agent_factory,
                max_concurrent=self.max_concurrent,
                output_path=self.output_path,
            )
        else:
            return await run_local(
                dataset=dataset,
                agent_factory=agent_factory,
                max_concurrent=self.max_concurrent,
                output_path=self.output_path,
            )
