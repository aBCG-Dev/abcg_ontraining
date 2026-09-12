import csv
import os
from django.core.management.base import BaseCommand
from questions.models import BcgVaccination

class Command(BaseCommand):
    help = 'Import BCG vaccinations from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"File {csv_path} does not exist"))
            return

        self.stdout.write(f"Starting import of {csv_path}...")
        
        # Clear the table first to have a clean import state
        BcgVaccination.objects.all().delete()
        self.stdout.write("Cleared existing BcgVaccination registry.")
        
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            vaccinations = []
            count = 0
            
            for row in reader:
                # Parse age
                age_val = None
                if row.get('age'):
                    try:
                        age_val = int(row['age'])
                    except ValueError:
                        pass
                
                # Create BcgVaccination object
                v = BcgVaccination(
                    beneficiary_id=row.get('beneficiary_id', '').strip(),
                    first_name=row.get('first_name', '').strip(),
                    last_name=row.get('last_name', '').strip(),
                    beneficiary_gender=row.get('beneficiary_gender', '').strip(),
                    ben_gender=row.get('ben_gender', '').strip(),
                    age=age_val,
                    ben_mobile_number=row.get('ben_mobile_number', '').strip(),
                    dob=row.get('dob', '').strip(),
                    date=row.get('date', '').strip(),
                    registration_mode=row.get('registration_mode', '').strip(),
                    vaccination_status=row.get('vaccination_status', '').strip(),
                    beneficiary_type_name=row.get('beneficiary_type_name', '').strip(),
                    address=row.get('address', '').strip(),
                    pincode=row.get('pincode', '').strip(),
                    facility_id=row.get('facility_id', '').strip(),
                    site_id=row.get('site_id', '').strip(),
                    approved_by=row.get('approved_by', '').strip(),
                    date_created=row.get('date_created', '').strip()
                )
                vaccinations.append(v)
                count += 1
                
                if len(vaccinations) >= 500:
                    BcgVaccination.objects.bulk_create(vaccinations, ignore_conflicts=True)
                    vaccinations = []
            
            if vaccinations:
                BcgVaccination.objects.bulk_create(vaccinations, ignore_conflicts=True)
                
        self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} BCG vaccination records."))
