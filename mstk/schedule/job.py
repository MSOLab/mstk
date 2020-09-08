from typing import List, Dict, Any, Iterator, Callable

from mstk.schedule.activity import Operation

__all__ = ["Job"]


class Job:
    """A container for job information"""

    __slots__ = ["__job_id", "__operation_list", "__contents"]

    def __init__(self, job_id):
        self.__job_id: str = job_id
        self.__operation_list: List[Operation] = []
        self.__contents: Dict[str, Any] = {}

    @property
    def job_id(self) -> str:
        return self.__job_id

    @property
    def operation_list(self) -> List[Operation]:
        return self.__operation_list

    @property
    def contents(self) -> Dict[str, Any]:
        return self.__contents

    def add_operation(self, operation: Operation):
        """Adds an operation to the operation list

        Args:
            operation (Operation): an operation to be added
        """
        if operation in self.operation_list:
            raise KeyError(
                f"Operation {operation.ac_id} exists in job {self.job_id}"
            )
        self.operation_list.append(operation)

    def remove_operation(self, operation: Operation):
        """Removes an operation to the operation list

        Args:
            operation (Operation): an operation to be removed
        """
        self.operation_list.remove(operation)

    def oper_iter(self) -> Iterator[Operation]:
        """
        Yields:
            Iterator[Operation]
        """
        for operation in self.operation_list:
            yield operation

    def add_contents(self, key: str, value: Any):
        """Adds supplementary information of the job to a dictionary [contents]

        Args:
            key (str): an id for the content
            value (Any): the value to be stored
        """
        self.contents[key] = value

    def display_contents(self, func: Callable, **kwargs):
        """Prints all the contents (default)"""
        func(self.contents)
