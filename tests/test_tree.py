from pprint import pprint
from unittest import TestCase

from src.mindmap.tree import *


class TestTree(TestCase):

    def test_without_leaves(self):
        a_tree = tree()
        a_tree['a']['b']
        a_tree_wh_leaves = without_leaves(a_tree)
        
        another_tree = tree()
        another_tree['a']
        
        print()
        pprint(a_tree)
        pprint(a_tree_wh_leaves)
        pprint(another_tree)

        self.assertEqual(a_tree_wh_leaves, another_tree)
