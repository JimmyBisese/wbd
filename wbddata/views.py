
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django.db.models import IntegerField
from django.db.models.functions import Cast
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from .models import HUC, WBD
from .serializers import HUCSerializer, WBDSerializer # , HUC12Serializer

'''
	'code' can be anything from a Region (2-digits) to a Subwatershed (12-digit)
	If it is lower than a subwatershed it returns data for the next level.  
	If it is a subwatershed, it returns summary data for upstream (default) or downstream navigation
	The terms are defined in https://nhd.usgs.gov/wbd_facts.html

	Watershed Definitions
	Name			Level	Digit	Number of HUCs
	Region			1		2		21
	Subregion		2		4		222
	Basin			3		6		352
	Subbasin		4		8		2,149
	Watershed		5		10		22,000
	Subwatershed	6		12		160,000

    The pagination code comes from 
        https://stackoverflow.com/questions/35625251/how-do-you-use-pagination-in-a-django-rest-framework-viewset-subclass/46173281#46173281

'''


'''

    used to overwrite viewset and add one extra pagination thing
    
'''
class mReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    def get_paginated_data(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_data(data)

'''

    Base Class for the HUC###ViewSets

'''
class HUCViewSet(mReadOnlyModelViewSet):

    lookup_field = 'huc_code'

    serializer_class = HUCSerializer
    queryset = HUC.objects.all()
    ordering = ('huc_code',)
    huc_label = 'Region'
    hudigit = 2

    '''
        "lists" the Hydrologic Units at the selected hudigit level, with pagination
        regions 01, 02, 03, 04, ...
    '''
    def list(self, request, *args, **kwargs):
        if request.method == 'GET':
            hudigit_nu = self.hudigit
            if kwargs and 'huc_code' in kwargs:
                self.queryset = HUC.objects.filter(huc_code__exact=kwargs['huc_code'])
                hudigit_nu = len(kwargs['huc_code'])

            serializer_context = {
                'request': request,
            }

            serializer = self.get_serializer(self.paginate_queryset(self.queryset), many=True, hudigit_nu=hudigit_nu)

            response = {
                'code': status.HTTP_200_OK,
                'USGS HUC Level': self.huc_label,
                'HUDigit Domain': self.hudigit,
            }
            count = len(serializer.data)
            if count == 1:
                data = serializer.data[0]
                drilldown_url = data['drilldown_url'] if 'drilldown_url' in data else None
                response = {
                    'code': status.HTTP_200_OK,
                    'USGS HUC Level': self.huc_label,
                    'HUDigit Domain': self.hudigit,
                    'huc_code': data['huc_code'],
                    'name': data['name'],
                    'drilldown_url': drilldown_url,
                    # 'detail_url': data['detail_url'],
                }
            else:
                #jab -- this is a custom function, and relies on a custom paginator
                custom_data = self.get_paginated_data(serializer.data)
                response = {
                    'code': status.HTTP_200_OK,
                    'USGS HUC Level': self.huc_label,
                    'HUDigit Domain': self.hudigit,
                }
                if custom_data['next'] or custom_data['previous']:
                    response['next'] = custom_data['next']
                    response['previous'] = custom_data['previous']
                response['count'] = custom_data['count']
                response['results'] = custom_data['results']

            return Response(response)

    @action(detail=True)
    def drilldown(self, request, *args, **kwargs):
        if request.method == 'GET':
            # this has to be true - that is how you get into the function
            if kwargs and 'huc_code' in kwargs:
                hudigit_nu = len(kwargs['huc_code'])

                def huc_type(argument):
                    switcher = {
                        2:  "Region",
                        4:  "Subregion",
                        6:  "AccountingUnit",
                        8:  "CatalogingUnit",
                        12: "Subwatershed",
                    }
                    return switcher.get(argument, "Invalid month")

                huc_type_match_tx = huc_type(hudigit_nu + 2)

                parent_queryset = HUC.objects.filter(huc_code__exact=kwargs['huc_code'])
                parent_data = self.get_serializer(parent_queryset[0], many=False, hudigit_nu=hudigit_nu).data

                '''
                    get all of the next level-down that start with the huc_code
                '''
                self.queryset = HUC.objects.filter(huc_type__exact=huc_type_match_tx, huc_code__startswith=kwargs['huc_code']).annotate(
                    huc_code_int=Cast('huc_code', IntegerField())
                ).order_by('huc_code_int', 'huc_code')
                self.huc_label = huc_type_match_tx
                self.hudigit = hudigit_nu + 2

            serializer_context = {
                'request': request,
            }

            data = None
            page = request.GET.get('page')
            try:
                page = self.paginate_queryset(self.queryset)
            except Exception as e:
                page = []
                data = page
                return Response({
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": 'No more record.',
                    "data" : data
                    })

            if page is not None:
                serializer = self.get_serializer(page, many=True, hudigit_nu=hudigit_nu)
                data = serializer.data
                # return self.get_paginated_response(data)
                response = {
                    'code': status.HTTP_200_OK,
                    'USGS HUC Level': self.huc_label,
                    'HUDigit Domain': self.hudigit,
                }
                if kwargs and 'huc_code' in kwargs:
                    response['parent'] = parent_data

                #jab -- this is a custom function, and relies on a custom paginator
                custom_data = self.get_paginated_data(data)
                if custom_data['next'] or custom_data['previous']:
                    response['next'] = custom_data['next']
                    response['previous'] = custom_data['previous']
                response['count'] = custom_data['count']
                response['results'] = custom_data['results']

                return Response(response)

            return Response({
                "status": status.HTTP_200_OK,
                "message": 'Sitting records.',
                "data" : data
            })


class HUCRegionViewSet(HUCViewSet):
    queryset = HUC.objects.filter(huc_type__exact="Region").annotate(
        huc_code_int=Cast('huc_code', IntegerField())
    ).order_by('huc_code_int', 'huc_code')
    huc_label = 'Region'
    hudigit = 2
    lookup_field = 'huc_code'

class HUCSubregionViewSet(HUCViewSet):
    queryset = HUC.objects.filter(huc_type__exact="Subregion").annotate(
        huc_code_int=Cast('huc_code', IntegerField())
    ).order_by('huc_code_int', 'huc_code')
    huc_label = 'Subregion'
    hudigit = 4
    lookup_field = 'huc_code'

class HUCAccountingUnitViewSet(HUCViewSet):
    queryset = HUC.objects.filter(huc_type__exact="AccountingUnit").annotate(
        huc_code_int=Cast('huc_code', IntegerField())
    ).order_by('huc_code_int', 'huc_code')
    huc_label = 'AccountingUnit'
    hudigit = 6

class PageNumberPaginationDataOnly(PageNumberPagination):
    # Set any other options you want here like page_size

    def get_paginated_response(self, data):
        return Response(data)

class HUCCatalogingUnitViewSet(HUCViewSet):
    queryset = HUC.objects.filter(huc_type__exact="CatalogingUnit").annotate(
                    huc_code_int=Cast('huc_code', IntegerField())).order_by('huc_code_int', 'huc_code')
    huc_label = 'CatalogingUnit'
    hudigit = 8
    serializer_class = HUCSerializer

    # this provides the 'drill-down' behavior
    # it is using the WBD instead of the HUC model, since its getting hu12
    @action(detail=True)
    def drilldown(self, request, *args, **kwargs):
        view_name = 'testing'
        if request.method == 'GET':
            if kwargs and 'huc_code' in kwargs:
                self.queryset = WBD.objects.filter(huc_code__startswith=kwargs['huc_code']).annotate(
                    huc_code_int=Cast('huc_code', IntegerField())
                ).order_by('huc_code_int')
                self.huc_label = 'Subwatershed'
                self.hudigit = 12
            serializer_context = {
                'request': request,
            }
            data = None
            page = request.GET.get('page')
            try:
                page = self.paginate_queryset(self.queryset)
            except Exception as e:
                page = []
                data = page
                return Response({
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": 'No more record.',
                    "data" : data
                    })

            if page is not None:
                serializer = self.get_serializer(page, many=True, hudigit_nu=8)
                # serializer_class = WBDSerializer
                #
                # # serializer_class = self.get_serializer_class()
                # kwargs['context'] = self.get_serializer_context()
                # si = serializer_class(*args, **kwargs)
                #
                # serializer = si(page, many=True)
                data = serializer.data

                response = {
                    'code': status.HTTP_200_OK,
                    'USGS HUC Level': self.huc_label,
                    'HUDigit Domain': self.hudigit,
                }
                if kwargs and 'hu8' in kwargs:
                    response['parent'] = kwargs['hu8']
                #jab -- this is a custom function, and relies on a custom paginator
                custom_data = self.get_paginated_data(data)
                response['next'] = custom_data['next']
                response['previous'] = custom_data['previous']
                response['count'] = custom_data['count']
                response['children'] = custom_data['results']

                return Response(response)

            return Response({
                "status": status.HTTP_200_OK,
                "message": 'Sitting records.',
                "data" : data
            })

class HUCSubwatershedViewSet(mReadOnlyModelViewSet):
    queryset = WBD.objects.all().annotate(
        huc_code_int=Cast('huc_code', IntegerField())
    ).order_by('huc_code_int', 'huc_code')
    serializer_class = WBDSerializer
    huc_label = 'Subwatershed'
    hudigit = 12

    # this list hu12 HUC12s
    def list(self, request, *args, **kwargs):

        if request.method == 'GET':
            if kwargs and 'huc_code' in kwargs:
                self.queryset = WBD.objects.filter(huc_code__startswith=kwargs['huc_code']).annotate(
                    huc_code_int=Cast('huc_code', IntegerField())
                ).order_by('huc_code_int')
                self.huc_label = 'Subwatershed'
                self.hudigit = 12
            serializer_context = {
                'request': request,
            }

            data = None
            page = request.GET.get('page')
            try:
                page = self.paginate_queryset(self.queryset)
            except Exception as e:
                page = []
                data = page
                return Response({
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": 'No more record.',
                    "data" : data
                    })

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = serializer.data
                return self.get_paginated_response(data)


            return Response({
                "status": status.HTTP_200_OK,
                "message": 'Sitting records.',
                "data" : data
            })

class HUCSubwatershedList(generics.ListAPIView):
    serializer_class = WBDSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned HU12 (WBD),
        by filtering against a query parameter in the URL.
        """
        queryset = WBD.objects.all()
        huc_code = None
        if 'hu12' in self.kwargs:
            huc_code = self.kwargs['hu12']
        elif 'huc_code' in self.kwargs:
            huc_code = self.kwargs['huc_code']
        if huc_code:
            if len(huc_code) == 12:
                queryset = queryset.filter(huc_code__exact=huc_code)
                paginate_by = None
                paginate_by_param = None
            else:
                queryset = queryset.filter(huc_code__startswith=huc_code)

        return queryset