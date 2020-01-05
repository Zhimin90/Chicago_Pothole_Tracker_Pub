from django.contrib.gis.db import models

class WorldBorder(models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile.
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.IntegerField('Population 2005')
    fips = models.CharField('FIPS Code', max_length=2)
    iso2 = models.CharField('2 Digit ISO', max_length=2)
    iso3 = models.CharField('3 Digit ISO', max_length=3)
    un = models.IntegerField('United Nations Code')
    region = models.IntegerField('Region Code')
    subregion = models.IntegerField('Sub-Region Code')
    lon = models.FloatField()
    lat = models.FloatField()

    # GeoDjango-specific: a geometry field (MultiPolygonField)
    mpoly = models.MultiPolygonField()

    # Returns the string representation of the model.
    def __str__(self):
        return self.name

class T_Potholes(models.Model):
    ADDRESS = models.CharField(max_length=100)
    REQUEST_DATE = models.DateTimeField()
    COMPLETION_DATE = models.DateTimeField()
    NUMBER_OF_POTHOLES_FILLED_ON_BLOCK = models.IntegerField()
    LATITUDE = models.DecimalField(null=True, blank=True, max_digits=9, decimal_places=6)
    LONGITUDE = models.DecimalField(null=True, blank=True, max_digits=9, decimal_places=6)
    LOCATION = models.PointField(null=True, blank=True,)

class Density_Map(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    poly_coordinate =  models.GeometryField(null=True, blank=True)
    density = models.DecimalField(null=True, blank=True, max_digits=40, decimal_places=20)
