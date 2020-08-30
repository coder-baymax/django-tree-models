import json

from django.db import connection
from django.test import TestCase, override_settings

from adjacency_list.models import Node


class TreeTest(TestCase):

    def get_sons(self, root):
        return {'name': root.name, 'update_time': root.update_time.timestamp(),
                'sons': [self.get_sons(x) for x in Node.objects.filter(parent=root)]}

    def get_sons_bfs(self, root):
        index, node_list = 0, [root]
        while index < len(node_list):
            temp_len = len(node_list)
            for node in Node.objects.filter(parent_id__in=[x.id for x in node_list[index:]]):
                node_list.append(node)
            index = temp_len
        node_dict = {x.id: {'name': x.name, 'parent_id': x.parent_id, 'sons': []}
                     for x in node_list}
        for node in node_dict.values():
            if node['parent_id']:
                node_dict[node['parent_id']]['sons'].append(node)
        return node_dict[root.id]

    def setUp(self) -> None:
        super(TreeTest, self).setUp()
        self.root_node = Node.objects.create(name='root')
        for i in range(3):
            parent = self.root_node
            for j in range(3):
                parent = Node.objects.create(name='sons_{}_{}'.format(i, j), parent=parent)

    @override_settings(DEBUG=True)
    def test_scan(self):
        self.get_sons(self.root_node)
        for item in connection.queries:
            print(item)

    @override_settings(DEBUG=True)
    def test_scan_bfs(self):
        ret = self.get_sons_bfs(self.root_node)
        for item in connection.queries:
            print(item)
