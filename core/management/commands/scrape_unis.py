import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from core.models import University

class Command(BaseCommand):
    help = 'Scrape universities from Wikipedia and save to database'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('starting the collection Uni Data from internet'))
        url = 'https://en.wikipedia.org/wiki/List_of_universities_in_Germany'
        
        # 1. إضافة User-Agent لخداع الموقع بأنه متصفح حقيقي
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            # إرسال الطلب مع إضافة الـ headers
            response = requests.get(url, headers=headers)
            
            # التحقق من نجاح الاتصال (كود 200 يعني نجاح)
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Eror While connection  {response.status_code}'))
                return

            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'class': 'wikitable'})

            # 2. حماية الكود: التأكد من أن الجدول موجود فعلاً قبل سحب البيانات
            if not table:
                self.stdout.write(self.style.ERROR('Can\'t find the table in the pageweb '))
                return

            rows = table.find_all('tr')[1:]
            count = 0
            
            for row in rows:
                cols = row.find_all('td')
                # التأكد من أن الصف يحتوي على بيانات 
                if len(cols) > 0:
                    uni_name = cols[0].text.strip()
                    
                    uni, created = University.objects.get_or_create(
                        name=uni_name,
                        defaults={
                            'country': 'Germany',
                            'website_url': f'https://www.google.com/search?q={uni_name} official website'
                        }
                    )
                    
                    if created:
                        count += 1
                        self.stdout.write(self.style.SUCCESS(f'Aded Done: {uni_name}'))

            self.stdout.write(self.style.SUCCESS(f'Seccsefull! Added and withdrawn {count} Germen Collage to the DataBase'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An Eror doesn\'t exepted {e}'))