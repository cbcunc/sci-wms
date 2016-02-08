# -*- coding: utf-8 -*-
from contextlib import contextmanager

import os
import rtree
import bisect
import netCDF4 as nc4

from django.conf import settings
from pyaxiom.netcdf import EnhancedDataset, EnhancedMFDataset

from wms.utils import find_appropriate_time
from wms.models import VirtualLayer, Layer, Style


def try_float(obj):
    try:
        return int(obj)
    except ValueError:
        return None


class NetCDFDataset(object):

    @contextmanager
    def dataset(self):
        try:
            # Dataset is already loaded
            self._dataset.variables
            yield self._dataset
        except AttributeError:
            try:
                self._dataset = EnhancedDataset(self.path())
                yield self._dataset
            except RuntimeError:
                try:
                    self._dataset = EnhancedMFDataset(self.path(), aggdim='time')
                    yield self._dataset
                except (IndexError, RuntimeError):
                    yield None

    @contextmanager
    def topology(self):
        try:
            self._topology.variables
            yield self._topology
        except AttributeError:
            try:
                self._topology = EnhancedDataset(self.topology_file)
                yield self._topology
            except RuntimeError:
                yield None

    def close(self):
        try:
            self._dataset.close()
        except BaseException:
            pass

        try:
            self._topology.close()
        except BaseException:
            pass

    def has_cache(self):
        return os.path.exists(self.topology_file)

    @property
    def topology_file(self):
        return os.path.join(settings.TOPOLOGY_PATH, '{}.nc'.format(self.safe_filename))

    @property
    def domain_file(self):
        return os.path.join(settings.TOPOLOGY_PATH, '{}.domain'.format(self.safe_filename))

    @property
    def node_tree_root(self):
        return os.path.join(settings.TOPOLOGY_PATH, '{}.nodes').format(self.safe_filename)

    @property
    def node_tree_data_file(self):
        return '{}.dat'.format(self.node_tree_root)

    @property
    def node_tree_index_file(self):
        return '{}.idx'.format(self.node_tree_root)

    @property
    def face_tree_root(self):
        return os.path.join(settings.TOPOLOGY_PATH, '{}.faces').format(self.safe_filename)

    @property
    def face_tree_data_file(self):
        return '{}.dat'.format(self.face_tree_root)

    @property
    def face_tree_index_file(self):
        return '{}.idx'.format(self.face_tree_root)

    def setup_getfeatureinfo(self, ncd, variable_object, request, location=None):

        location = location or 'face'

        try:
            latitude = request.GET['latitude']
            longitude = request.GET['longitude']
            # Find closest cell or node (only node for now)
            if location == 'face':
                tree = rtree.index.Index(self.face_tree_root)
            elif location == 'node':
                tree = rtree.index.Index(self.node_tree_root)
            else:
                raise NotImplementedError("No RTree for location '{}'".format(location))
            nindex = list(tree.nearest((longitude, latitude, longitude, latitude), 1, objects=True))[0]
            closest_x, closest_y = tuple(nindex.bbox[2:])
            geo_index = nindex.object
        except BaseException:
            raise
        finally:
            tree.close()

        # Get time indexes
        time_var_name = find_appropriate_time(variable_object, ncd.get_variables_by_attributes(standard_name='time'))
        time_var = ncd.variables[time_var_name]
        if hasattr(time_var, 'calendar'):
            calendar = time_var.calendar
        else:
            calendar = 'gregorian'
        start_nc_num = round(nc4.date2num(request.GET['starting'], units=time_var.units, calendar=calendar))
        end_nc_num = round(nc4.date2num(request.GET['ending'], units=time_var.units, calendar=calendar))

        all_times = time_var[:]
        start_nc_index = bisect.bisect_right(all_times, start_nc_num)
        end_nc_index = bisect.bisect_right(all_times, end_nc_num)

        try:
            all_times[start_nc_index]
        except IndexError:
            start_nc_index = all_times.size - 1
        try:
            all_times[end_nc_index]
        except IndexError:
            end_nc_index = all_times.size - 1

        if start_nc_index == end_nc_index:
            if start_nc_index > 0:
                start_nc_index -= 1
            elif end_nc_index < all_times.size:
                end_nc_index += 1
        return_dates = nc4.num2date(all_times[start_nc_index:end_nc_index], units=time_var.units, calendar=calendar)

        return geo_index, closest_x, closest_y, start_nc_index, end_nc_index, return_dates

    def __del__(self):
        self.close()

    def analyze_virtual_layers(self):
        with self.dataset() as nc:
            if nc is not None:
                # Earth Projected Sea Water Velocity
                u_names = ['eastward_sea_water_velocity', 'eastward_sea_water_velocity_assuming_no_tide']
                v_names = ['northward_sea_water_velocity', 'northward_sea_water_velocity_assuming_no_tide']
                us = nc.get_variables_by_attributes(standard_name=lambda v: v in u_names)
                vs = nc.get_variables_by_attributes(standard_name=lambda v: v in v_names)
                VirtualLayer.make_vector_layer(us, vs, 'sea_water_velocity', 'vectors', self.id)

                # Grid projected Sea Water Velocity
                u_names = ['x_sea_water_velocity', 'grid_eastward_sea_water_velocity']
                v_names = ['y_sea_water_velocity', 'grid_northward_sea_water_velocity']
                us = nc.get_variables_by_attributes(standard_name=lambda v: v in u_names)
                vs = nc.get_variables_by_attributes(standard_name=lambda v: v in v_names)
                VirtualLayer.make_vector_layer(us, vs, 'grid_sea_water_velocity', 'vectors', self.id)

                # Earth projected Winds
                u_names = ['eastward_wind']
                v_names = ['northward_wind']
                us = nc.get_variables_by_attributes(standard_name=lambda v: v in u_names)
                vs = nc.get_variables_by_attributes(standard_name=lambda v: v in v_names)
                VirtualLayer.make_vector_layer(us, vs, 'winds', 'barbs', self.id)

                # Grid projected Winds
                u_names = ['x_wind', 'grid_eastward_wind']
                v_names = ['y_wind', 'grid_northward_wind']
                us = nc.get_variables_by_attributes(standard_name=lambda v: v in u_names)
                vs = nc.get_variables_by_attributes(standard_name=lambda v: v in v_names)
                VirtualLayer.make_vector_layer(us, vs, 'grid_winds', 'barbs', self.id)

                # Earth projected Ice velocity
                u_names = ['eastward_sea_ice_velocity']
                v_names = ['northward_sea_ice_velocity']
                us = nc.get_variables_by_attributes(standard_name=lambda v: v in u_names)
                vs = nc.get_variables_by_attributes(standard_name=lambda v: v in v_names)
                VirtualLayer.make_vector_layer(us, vs, 'sea_ice_velocity', 'vectors', self.id)

    def process_layers(self):
        with self.dataset() as nc:
            if nc is not None:

                for v in nc.variables:
                    l, _ = Layer.objects.get_or_create(dataset_id=self.id, var_name=v)

                    nc_var = nc.variables[v]
                    if hasattr(nc_var, 'valid_range'):
                        l.default_min = try_float(nc_var.valid_range[0])
                        l.default_max = try_float(nc_var.valid_range[-1])
                    # valid_min and valid_max take presendence
                    if hasattr(nc_var, 'valid_min'):
                        l.default_min = try_float(nc_var.valid_min)
                    if hasattr(nc_var, 'valid_max'):
                        l.default_max = try_float(nc_var.valid_max)

                    if hasattr(nc_var, 'standard_name'):
                        std_name = nc_var.standard_name
                        l.std_name = std_name

                        if len(nc_var.dimensions) > 1:
                            l.active = True

                    if hasattr(nc_var, 'long_name'):
                        l.description = nc_var.long_name

                    if hasattr(nc_var, 'units'):
                        l.units = nc_var.units

                    # Set some standard styles
                    l.styles = Style.defaults()
                    l.save()

        self.analyze_virtual_layers()

    def nearest_time(self, layer, time):
        """
        Return the time index and time value that is closest
        """
        with self.dataset() as nc:
            time_vars = nc.get_variables_by_attributes(standard_name='time')
            if len(time_vars) == 1:
                time_var = time_vars[0]
            else:
                # if there is more than variable with standard_name = time
                # fine the appropriate one to use with the layer
                var_obj = nc.variables[layer.access_name]
                time_var_name = find_appropriate_time(var_obj, time_vars)
                time_var = nc.variables[time_var_name]
            units = time_var.units
            if hasattr(time_var, 'calendar'):
                calendar = time_var.calendar
            else:
                calendar = 'gregorian'
            num_date = round(nc4.date2num(time, units=units, calendar=calendar))

            times = time_var[:]
            time_index = bisect.bisect_right(times, num_date)
            try:
                times[time_index]
            except IndexError:
                time_index -= 1
            return time_index, times[time_index]
