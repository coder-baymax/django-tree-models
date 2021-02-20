import json

from django.db import connection
from django.test import TestCase, override_settings

from nested_sets.models import Node, NodeRelation


class TreeTest(TestCase):

    def setUp(self) -> None:
        super(TreeTest, self).setUp()
        self.root_node = Node.objects.create_with_relation(name='root')
        for i in range(2):
            parent = self.root_node
            for j in range(3):
                parent = Node.objects.create_with_relation(
                    name='sons_{}_{}'.format(i, j), parent_id=parent.id)

    def test_get(self):
        print(Node.objects.get_tree(self.root_node.id))

    def test_delete(self):
        for item in NodeRelation.objects.all():
            print(item.id, item.ancestor, item.descendant, item.id)

    @override_settings(DEBUG=True)
    def test_move(self):
        Node.objects.move_with_relation(2, 6)
        print(json.dumps(Node.objects.get_tree(1), indent=2))
        for item in connection.queries:
            print(item)
