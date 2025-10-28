import pytest
from pytest_examples import CodeExample, EvalExample, find_examples


@pytest.mark.parametrize("example", find_examples("tests/examples"), ids=str)
def test_pytest_example(example: CodeExample, eval_example: EvalExample):
    if eval_example.update_examples:
        print("Running example from:", example.path)
        eval_example.format(example)
        eval_example.run_print_update(example)
    else:
        eval_example.lint(example)
        print("Running example from:", example.path)
        eval_example.run_print_check(example)
