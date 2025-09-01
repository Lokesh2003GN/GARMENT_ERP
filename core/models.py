from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    type = models.CharField(max_length=15)
    phone1 = models.CharField(max_length=15)
    phone2 = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.username
       
    @property
    def is_owner(self):
    	return hasattr(self, 'company')
    @property
    def is_staff_user(self):
        return hasattr(self, 'staff')
    
    @property
    def is_weaver(self):
        return self.is_staff_user and self.staff.role.lower() == 'weaver'

    @property
    def is_warper(self):
        return self.is_staff_user and self.staff.role.lower() == 'warper'
        
class Company(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.TextField()
    def __str__(self):
    	return f"{self.owner} - {self.name}"
    
  
class Staff(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)
    def __str__(self):
    	return f"{self.user.username} ({self.company.name})"
    	
class Yarn(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    color = models.CharField(null=True, blank=False, max_length=150)
    count = models.FloatField()

    def __str__(self):
        return f"{self.color} ({self.count}s)"
    	

class WarpDesign(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.name} - ({self.company})"
class WarpDesignEntry(models.Model):
    warp_design = models.ForeignKey(WarpDesign, on_delete=models.CASCADE, related_name='entries')
    order = models.FloatField()
    yarn = models.ForeignKey(Yarn, on_delete=models.CASCADE)
    lint_count = models.FloatField()
    color = models.CharField(max_length=7)  # Store hex color (e.g., #ff0000)

    def __str__(self):
        return f"{self.yarn} - {self.lint_count} - {self.color}"
    


class Warp(models.Model):
    design = models.ForeignKey(WarpDesign, on_delete=models.CASCADE, related_name='design')
    warper = models.ForeignKey(CustomUser, related_name="warper", on_delete=models.CASCADE, null=True, blank=True)
    weaver = models.ForeignKey(CustomUser, related_name="weaver", on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(null=True, blank=True, max_length=150)
    meters = models.FloatField(null=True, blank=False)
    date_start_warper = models.DateField(null=True, blank=True)
    date_start_weaver = models.DateField(null=True, blank=True)
    length = models.FloatField(null=True, blank=True)
    isComplected = models.BooleanField(default=False)
    isWarped = models.BooleanField(default=False)
    warp_wage = models.FloatField(null=True, blank=True)
    warp_yarn = models.FloatField(null=True, blank=False)
    isSecondary = models.BooleanField(default=False)

    primary_warp = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='secondary_warps'
    )

    class Meta:
        ordering = ['-date_start_warper', '-date_start_weaver']

    
class Piece(models.Model):
    date = models.DateField()
    count = models.FloatField()
    length = models.FloatField(null=True, blank=True)
    warp = models.ForeignKey(Warp, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=10,
        choices=[('good', 'Good'), ('demage', 'Demage'), ('extra', 'Extra'), ('return', 'Return')],
        default='good'
    )
    def __str__(self):
        return f"Piece {self.warp}"


        return f"Wage {self.pk}"
class Wage(models.Model):
    warp = models.ForeignKey(Warp, on_delete=models.CASCADE, related_name='wage_entries')
    date = models.DateField()
    wage_good = models.FloatField()
    wage_demage = models.FloatField()
    wage_extra = models.FloatField()
    def __str__(self):
        return f"Wage {self.pk}"
       
           
class Transactions(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.DateField(null=False, blank=False)
    staff = models.ForeignKey(CustomUser, related_name="staff_wage",on_delete=models.CASCADE)
    note = models.CharField(null=True, blank=True, max_length=150)
    amount = models.FloatField(null=False, blank=False)

    def __str__(self):
        return f"Transaction {self.pk}"
    



    
class Yarn_Transactions(models.Model):
    yarn = models.ForeignKey(Yarn, related_name="yarn_transactions", on_delete=models.CASCADE) # Renamed related_name for clarity
    date = models.DateField(null=False, blank=False)
    quantity = models.FloatField()
    warp = models.ForeignKey(Warp, related_name="warp_transactions", on_delete=models.CASCADE, null=True, blank=True)
    transaction_type = models.CharField(
        max_length=10,
        choices=[('give', 'Give'), ('buy', 'Buy')],
        default='give'
    )
    to = models.CharField(
        max_length=10,
        choices=[('warper', 'Warper'), ('weaver', 'Weaver')]
    )
    note = models.CharField(null=True, blank=True, max_length=150)

    def __str__(self):
        return f"{self.transaction_type} {self.quantity} of {self.yarn.color} on {self.date}"