from collections import defaultdict
from datetime import datetime

from django.db import models
from django.db.models import Subquery


class NodeManager(models.Manager):

    def create_with_relation(self, parent_id=None, **kwargs):
        node = self.create(**kwargs)
        relations = [] if parent_id is None else [NodeRelation(
            ancestor_id=x.ancestor_id, descendant=node, level=x.level + 1
        ) for x in NodeRelation.objects.filter(descendant=parent_id)]
        relations.append(NodeRelation(ancestor=node, descendant=node, level=0))
        NodeRelation.objects.bulk_create(relations)
        return node

    def delete_with_relation(self, node_id):
        node_ids = [x['descendant_id'] for x in NodeRelation.objects.filter(
            ancestor_id=node_id).values('descendant_id')]
        self.filter(id__in=node_ids).delete()

    def get_tree(self, node_id):
        node_dict = defaultdict(lambda: {'name': '', 'sons': []})
        for node in Node.objects.filter(descendant__ancestor_id=node_id):
            node_dict[node.id]['name'] = node.name
        for relation in NodeRelation.objects.filter(level=1, descendant_id__in=node_dict.keys()):
            node_dict[relation.ancestor_id]['sons'].append(node_dict[relation.descendant_id])
        return node_dict[node_id]

    def move_with_relation(self, node_id, parent_id):
        ancestor_query = ~models.Q(ancestor_id=node_id) & models.Q(ancestor_id__in=Subquery(
            NodeRelation.objects.filter(descendant_id=node_id).values('ancestor_id')))
        descendant_query = models.Q(descendant_id__in=Subquery(
            NodeRelation.objects.filter(ancestor_id=node_id).values('descendant_id')))
        NodeRelation.objects.filter(ancestor_query & descendant_query).delete()

        ancestor_list = list(NodeRelation.objects.filter(descendant_id=parent_id))
        descendant_list = list(NodeRelation.objects.filter(ancestor_id=node_id))
        new_relations = [NodeRelation(
            ancestor_id=x.ancestor_id, descendant_id=y.descendant_id, level=x.level + y.level + 1
        ) for x in ancestor_list for y in descendant_list]
        NodeRelation.objects.bulk_create(new_relations)


class Node(models.Model):
    name = models.TextField(null=True, blank=True)
    update_time = models.DateTimeField(null=False, blank=False, default=datetime.utcnow)
    create_time = models.DateTimeField(null=False, blank=False, default=datetime.utcnow)

    objects = NodeManager()


class NodeRelation(models.Model):
    ancestor = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='ancestor')
    descendant = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='descendant')
    level = models.IntegerField(null=False, blank=False, db_index=True, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['ancestor', 'descendant'], name='unique_relation')
        ]
