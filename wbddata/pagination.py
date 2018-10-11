from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class WBDCustomPagination(PageNumberPagination):
    def get_paginated_data(self, data):
        return {
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        }