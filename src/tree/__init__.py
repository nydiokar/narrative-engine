"""Tree-based narrative workbench.

Branch, compare, promote, and prune nodes in a story development tree.
Each node wraps a frozen ContractStore snapshot + variant metadata.
"""

from src.tree.node import TreeNode
from src.tree.executor import TreeExecutor

__all__ = ["TreeNode", "TreeExecutor"]
