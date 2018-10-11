"""wbd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, re_path
from django.conf.urls import url, include

from rest_framework import routers


from .views import HUCRegionViewSet, HUCSubregionViewSet, HUCAccountingUnitViewSet, HUCCatalogingUnitViewSet, HUCSubwatershedViewSet
from .views import HUCSubwatershedList # WBDViewSet,


urlpatterns = [

    path(r'hu2/',  HUCRegionViewSet.as_view({'get': 'list'}),           name='region-ulist'),
    path(r'hu4/',  HUCSubregionViewSet.as_view({'get': 'list'}),        name='subregion-ulist'),
    path(r'hu6/',  HUCAccountingUnitViewSet.as_view({'get': 'list'}),   name='accountingunit-ulist'),
    path(r'hu8/',  HUCCatalogingUnitViewSet.as_view({'get': 'list'}),   name='catalogingunit-ulist'),
    path(r'hu12/', HUCSubwatershedViewSet.as_view({'get': 'list'}),     name='subwatershedvs-ulist'),

    re_path(r'huc/(?P<huc_code>\d{2})/drilldown/', HUCRegionViewSet.as_view({'get': 'drilldown'}), name='region-drilldown'),
    re_path(r'huc/(?P<huc_code>\d{4})/drilldown/', HUCSubregionViewSet.as_view({'get': 'drilldown'}), name='subregion-drilldown'),
    re_path(r'huc/(?P<huc_code>\d{6})/drilldown/', HUCAccountingUnitViewSet.as_view({'get': 'drilldown'}), name='accountingunit-drilldown'),
    re_path(r'huc/(?P<huc_code>\d{8})/drilldown/', HUCCatalogingUnitViewSet.as_view({'get': 'drilldown'}), name='catalogingunit-drilldown'),

    path(r'huc/',  HUCRegionViewSet.as_view({'get': 'list'}), name='region-list'),
    re_path(r'huc/(?P<huc_code>\d{2})/',  HUCRegionViewSet.as_view({'get': 'list'}), name='region-list'),
    re_path(r'huc/(?P<huc_code>\d{4})/', HUCSubregionViewSet.as_view({'get': 'list'}), name='subregion-list'),
    re_path(r'huc/(?P<huc_code>\d{6})/', HUCAccountingUnitViewSet.as_view({'get': 'list'}), name='accountingunit-list'),
    re_path(r'huc/(?P<huc_code>\d{8})/', HUCCatalogingUnitViewSet.as_view({'get': 'list'}), name='catalogingunit-list'),
    re_path(r'huc/(?P<huc_code>\d{12})/',  HUCSubwatershedViewSet.as_view({'get': 'list'}), name='subwatershed-detail'),

    # alternate methodology
    path(r'hu12List/', HUCSubwatershedList.as_view(), name='subwatershed-ulist'),

    path(r'api-auth/', include('rest_framework.urls', namespace='wbd_rest_framework')),
]


# Routers provide an easy way of automatically determining the URL conf.
# i couldn't get it working
# router = routers.DefaultRouter()
# router.register(r'huc', HUCRegionViewSet, base_name='region')
# # router.register(r'huc', HUCRegionViewSet, base_name='subregion')
# router.register(r'huc', HUCSubregionViewSet, base_name='subregion')
# router.register(r'accountingunit', HUCAccountingUnitViewSet)
# router.register(r'catalogingunit', HUCCatalogingUnitViewSet)

# these are repeated, but use the HU Digit Domain (EPA designatio)
# router.register(r'hu2',                          HUCRegionViewSet,          base_name='region-list')
# #router.register(r'hu2/(?P<hu2>\d{2})/drilldown', HUCRegionViewSet,          base_name='region-drilldown')
# router.register(r'hu4',                          HUCSubregionViewSet,       base_name='subregion-list')
# # router.register(r'hu4/(?P<hu2>\d{4})/drilldown', HUCSubregionViewSet,       base_name='subregion-drilldown')
# router.register(r'hu6',                          HUCAccountingUnitViewSet, base_name='accountingunit-list')
# #router.register(r'hu6/(?P<hu2>\d{6})/drilldown', HUCAccountingUnitViewSet, base_name='accountingunit-drilldown')
# router.register(r'hu8',                          HUCCatalogingUnitViewSet, base_name='catalogingunit-list')
# router.register(r'hu12',                          HUCSubwatershedViewSet, base_name='subwatershed-list')
#router.register(r'hu8/(?P<hu2>\d{8})/drilldown', HUCCatalogingUnitViewSet, base_name='catalogingunit-drilldown')
# ...
#     # path(r'', include(router.urls)),