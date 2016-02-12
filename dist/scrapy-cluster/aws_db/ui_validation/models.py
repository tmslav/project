from django.db import models

class Results(models.Model):
	status = models.CharField(max_length=20,default='unknown')
	search_name = models.CharField(max_length=200,default='none')
	timestamp = models.DateTimeField(auto_now=True)
	resultid = models.AutoField(primary_key=True)
	parts_found_in_rds = models.IntegerField(default=0)
	parts_send_to_hitlist = models.IntegerField(default=0)
	parts_found_by_hitlist_add_to_rds = models.IntegerField(default=0)
	parts_not_found = models.IntegerField(default=0)
	percent_found = models.IntegerField(default=0)
	in_queue = models.IntegerField(default=0)

class DetailModel(models.Model):
	id = models.AutoField(primary_key=True)
	csv_id = models.ForeignKey(Results,default=0)
	part_id = models.CharField(max_length=200)
	status = models.CharField(max_length=50,default='none')
	site_name = models.CharField(max_length=300,default='none')
	timestamp = models.DateTimeField(auto_now=True)
	url = models.CharField(max_length=300)
