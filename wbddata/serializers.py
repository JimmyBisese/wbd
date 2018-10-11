from .models import HUC, WBD
from rest_framework import routers, serializers, viewsets
import re
from rest_framework.reverse import reverse


def huc_type(argument):
    switcher = {
        2: "Region",
        4: "Subregion",
        6: "AccountingUnit",
        8: "CatalogingUnit",
        12: "Subwatershed",
    }
    return switcher.get(argument, "Invalid month")

class HUCSerializer(serializers.HyperlinkedModelSerializer):

    '''
        the list of states is attached to each region name. this removes them
        "New England Region (CT,ME,MA,NH,NY,RI,VT)"
        and it prepends the HUC Code
    '''

    name = serializers.SerializerMethodField()
    def get_name(self, obj):
        return re.sub(r'\s+\([^)]*\)', '', obj.name)

    long_name = serializers.SerializerMethodField()
    def get_long_name(self, obj):
        return obj.huc_code + ' ' + obj.name

    state_fip_codes = serializers.SerializerMethodField()
    def get_state_fip_codes(self, obj):
        state_codes_tx = obj.name[obj.name.find("(")+1:obj.name.find(")")]
        return state_codes_tx.split(",")

    drilldown_url = serializers.SerializerMethodField()
    def get_drilldown_url(self, obj):
        url_name = huc_type(len(obj.huc_code)).lower() + '-drilldown'
        url_kwargs = {'huc_code': obj.huc_code,}
        return reverse(url_name, kwargs=url_kwargs, request=self.context['request'])

    # detail_url = serializers.SerializerMethodField()
    # def get_detail_url(self, obj):
    #     url_name = huc_type(len(obj.huc_code)).lower() + '-list'
    #     url_kwargs = {'huc_code': obj.huc_code,}
    #     return reverse(url_name, kwargs=url_kwargs, request=self.context['request'])

    h2_url = serializers.SerializerMethodField()
    h4_url = serializers.SerializerMethodField()
    h6_url = serializers.SerializerMethodField()
    h8_url = serializers.SerializerMethodField()
    def get_h2_url(self, obj):
        return reverse(huc_type(2).lower() + '-list', kwargs={'huc_code':obj.huc_code[0:2]}, request=self.context['request'])
    def get_h4_url(self, obj):
        return reverse(huc_type(4).lower() + '-list', kwargs={'huc_code':obj.huc_code[0:4]}, request=self.context['request'])
    def get_h6_url(self, obj):
        return reverse(huc_type(6).lower() + '-list', kwargs={'huc_code':obj.huc_code[0:6]}, request=self.context['request'])
    def get_h8_url(self, obj):
        return reverse(huc_type(8).lower() + '-list', kwargs={'huc_code':obj.huc_code[0:8]}, request=self.context['request'])

    class Meta:
        model = HUC
        fields = ('huc_code', 'name', 'long_name', 'state_fip_codes', 'drilldown_url',
                  'h2_url', 'h4_url','h6_url','h8_url', )

    def __init__(self, *args, **kwargs):

        hudigit_nu = kwargs.pop('hudigit_nu', None)

        super(HUCSerializer, self).__init__(*args, **kwargs)

        if hudigit_nu and hudigit_nu > 0:
            for hud in (2, 4, 6, 8):
                if hud > hudigit_nu:
                    self.fields.pop('h' + str(hud) + '_url')
        if hudigit_nu and hudigit_nu == 8:
            self.fields.pop('drilldown_url')


# class HUC12Serializer(serializers.ModelSerializer):
#     '''
#         this one uses the WBD data instead of the HUC
#     '''
#     detail_url = serializers.SerializerMethodField()
#     def get_detail_url(self, obj):
#         depth = len(obj.huc_code)
#         url_kwargs = {
#             'huc_code': obj.huc_code,
#         }
#         url_name = 'region-drilldown'
#         if depth == 4:
#             url_name = 'subregion-drilldown'
#         elif depth == 6:
#             url_name = 'accountingunit-drilldown'
#         elif depth == 8:
#             url_name = 'catalogingunit-drilldown'
#         elif depth == 12:
#             url_name = 'subwatershed-detail'
#         return reverse(url_name, kwargs=url_kwargs, request=self.context['request'])
#
#
#     name = serializers.SerializerMethodField()
#
#     def get_name(self, obj):
#         return obj.huc_code + ' ' + obj.name
#
#     class Meta:
#         model = WBD
#         fields = ('huc_code', 'name', "area_sq_km", 'detail_url')
#
#     def __init__(self, *args, **kwargs):
#
#         hudigit_nu = kwargs.pop('hudigit_nu', None)
#
#         super(HUC12Serializer, self).__init__(*args, **kwargs)

# Serializers define the API representation.
class WBDSerializer(serializers.ModelSerializer):

    # url = serializers.HyperlinkedIdentityField(view_name='huc12-detail', read_only=True)
    detail_url = serializers.SerializerMethodField()
    def get_detail_url(self, obj):
        url_kwargs = { 'huc_code': obj.huc_code,}
        url_name = 'subwatershed-detail'
        return reverse(url_name, kwargs=url_kwargs, request=self.context['request'])

    class Meta:

        model = WBD
        fields = (
                "huc_code",
                "detail_url",
                "name",
                "area_sq_km",
                "water_area_sq_km",
                "comid",
                "huc12_ds",
                "distance_km",
                "traveltime_hrs",
                "multiple_outlet_bool",
                "sink_bool",
                "headwater_bool",
                "terminal_bool",
                "terminal_huc12_ds",
                "terminal_outlet_type_code",
                "huc12_ds_count_nu",
        )
        read_only_fields = [f.name for f in WBD._meta.get_fields()]

    def __init__(self, *args, **kwargs):

        hudigit_nu = kwargs.pop('hudigit_nu', None)
        huc_code = kwargs.pop('huc_code', None)
        super(WBDSerializer, self).__init__(*args, **kwargs)