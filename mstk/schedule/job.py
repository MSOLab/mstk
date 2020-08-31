from typing import List, Dict, Iterator
from mstk.schedule.activity import Operation


class Job:

    job_id: str
    contents: Dict[str, str]
    operation_list = List[Operation]

    def __init__(self, job_id):
        self.job_id = job_id
        self.operation_list = []
        self.contents = {}

    def add_operation(self, operation: Operation):
        """adds an operation to the operation list

        Args:
            operation (Operation): [an operation to be added]
        """
        if operation in self.operation_list:
            raise KeyError(
                f"Operation {operation.ac_id} exists in job {self.job_id}"
            )
        self.operation_list.append(operation)

    def remove_operation(self, operation: Operation):
        """removes an operation to the operation list

        Args:
            operation (Operation): [an operation to be removed]
        """
        self.operation_list.remove(operation)

    def oper_iter(self) -> Iterator:
        """
        Yields:
            Iterator[Operation]
        """
        for operation in self.operation_list:
            yield operation
