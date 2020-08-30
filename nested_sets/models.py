from collections import defaultdict
from datetime import datetime

from django.db import models
from django.db.models import Subquery


class NodeManager(models.Manager):

    def create_with_relation(self, parent_id=None, **kwargs):
        node = self.create(**kwargs)
        relations = [] if parent_id is None else [NodeRelation(
            ancestor_id=x.ancestor_id, posterity=node, level=x.level + 1
        ) for x in NodeRelation.objects.filter(posterity=parent_id)]
        relations.append(NodeRelation(ancestor=node, posterity=node, level=0))
        NodeRelation.objects.bulk_create(relations)
        return node

    def delete_with_relation(self, node_id):
        node_ids = [x['posterity_id'] for x in NodeRelation.objects.filter(
            ancestor_id=node_id).values('posterity_id')]
        self.filter(id__in=node_ids).delete()

    def get_tree(self, node_id):
        node_dict = defaultdict(lambda: {'name': '', 'sons': []})
        for relation in NodeRelation.objects.filter(level=1, posterity_id__in=Subquery(
                NodeRelation.objects.filter(ancestor_id=node_id).values('posterity_id'))):
            node_dict[relation.ancestor_id]['sons'].append(node_dict[relation.posterity_id])
        for node in self.filter(id__in=list(node_dict.keys())):
            node_dict[node.id]['name'] = node.name
        return node_dict[node_id]

    def move_with_relation(self, node_id, parent_id):
        ancestor_query = ~models.Q(ancestor_id=node_id) & models.Q(ancestor_id__in=Subquery(
            NodeRelation.objects.filter(posterity_id=node_id).values('ancestor_id')))
        posterity_query = models.Q(posterity_id__in=Subquery(
            NodeRelation.objects.filter(ancestor_id=node_id).values('posterity_id')))
        NodeRelation.objects.filter(ancestor_query & posterity_query).delete()

        ancestor_list = list(NodeRelation.objects.filter(posterity_id=parent_id))
        posterity_list = list(NodeRelation.objects.filter(ancestor_id=node_id))
        new_relations = [NodeRelation(
            ancestor_id=x.ancestor_id, posterity_id=y.posterity_id, level=x.level + y.level + 1
        ) for x in ancestor_list for y in posterity_list]
        NodeRelation.objects.bulk_create(new_relations)


class Node(models.Model):
    name = models.TextField(null=True, blank=True)
    update_time = models.DateTimeField(null=False, blank=False, default=datetime.utcnow)
    create_time = models.DateTimeField(null=False, blank=False, default=datetime.utcnow)

    objects = NodeManager()


class NodeRelation(models.Model):
    ancestor = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='ancestor')
    posterity = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='posterity')
    level = models.IntegerField(null=False, blank=False, db_index=True, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['ancestor', 'posterity'], name='unique_relation')
        ]
