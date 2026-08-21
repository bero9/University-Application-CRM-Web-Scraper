import time
from django.core.management.base import BaseCommand
from core.models import University, Program
from selenium import webdriver
from selenium.webdriver.common.by import By
from thefuzz import process, fuzz

class Command(BaseCommand):
    help = 'Scrape ALL programs, extract actual URLs, and dynamically create missing Universities'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting DAAD Web Scraper (FULL HARVEST MODE)... 🚀'))
        
        # تحميل الجامعات الحالية في قاموس
        db_universities = {uni.name: uni for uni in University.objects.all()}
        db_uni_names = list(db_universities.keys())
        
        options = webdriver.ChromeOptions()
        
        try:
            driver = webdriver.Chrome(options=options)
            # حذفنا فلتر اللغة (&lang%5B%5D=2) لكي يجلب الإنجليزية والألمانية والمختلطة
            url = 'https://www2.daad.de/deutschland/studienangebote/international-programmes/en/result/?q=&degree%5B%5D=2&limit=10&display=list'
            
            self.stdout.write(self.style.WARNING(f'Opening base URL...'))
            driver.get(url)
            self.stdout.write(self.style.WARNING('Waiting 8 seconds for JS to load...'))
            time.sleep(8) 
            
            added_count = 0
            current_page = 1
            
            # حلقة لا نهائية: ستستمر بالعمل حتى يختفي زر "Next" من الموقع!
            while True:
                self.stdout.write(self.style.SUCCESS(f'\n--- 📄 Scraping Page {current_page} ---'))
                
                cards = driver.find_elements(By.CSS_SELECTOR, 'a.list-inline-item, div.c-directory-result__item, div.result-list-item, article')
                
                for card in cards:
                    try:
                        raw_text = card.text.strip()
                        if not raw_text:
                            continue

                        parts = [p.strip() for p in raw_text.split('•')]
                        if len(parts) >= 3:
                            degree_level = parts[0]
                            program_title = parts[1]
                            scraped_university_name = parts[2]
                        else:
                            continue
                        
                        # === 1. استخراج الرابط الفعلي للبرنامج ===
                        try:
                            # البحث عن أول رابط (a href) داخل الصندوق
                            program_link = card.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                            if not program_link:
                                program_link = url
                        except:
                            program_link = url

                        # === 2. البناء الذاتي للجامعات (Dynamic Creation) ===
                        if db_uni_names: # التأكد أن القائمة ليست فارغة لتجنب الأخطاء
                            best_match, score = process.extractOne(scraped_university_name, db_uni_names, scorer=fuzz.WRatio)
                        else:
                            score = 0
                            best_match = ""
                        
                        if score >= 90:
                            university = db_universities[best_match]
                        else:
                            # الجامعة غير موجودة؟ ننشئها فوراً!
                            university, uni_created = University.objects.get_or_create(
                                name=scraped_university_name,
                                defaults={'country': 'Germany'}
                            )
                            if uni_created:
                                self.stdout.write(self.style.NOTICE(f'  [+] Created Missing University: {university.name}'))
                                # إضافتها للقاموس ليتعرف عليها السكريبت في البطاقات القادمة
                                db_universities[university.name] = university
                                db_uni_names.append(university.name)
                        
                        # === 3. إنشاء البرنامج وربطه ===
                        # === 3. إنشاء البرنامج وربطه ===
                        program, created = Program.objects.get_or_create(
                            title=program_title,
                            university=university,
                            defaults={
                                'degree_level': degree_level, 
                                'language': 'Varies', # <--- تم التغيير هنا ليعني "متغيرة/متعددة"
                                'program_url': program_link 
                            }
                        )
                        if created:
                            added_count += 1
                            self.stdout.write(self.style.SUCCESS(f'  -> Linked: [{program_title}] to ({university.name})'))

                    except Exception as e:
                        continue
                
                # === البحث عن زر "التالي" للانتقال للصفحة القادمة ===
                # === البحث عن زر "التالي" والهروب من فخ الدوران ===
                try:
                    # 1. نحفظ الرابط الحالي قبل الضغط
                    previous_url = driver.current_url 
                    
                    css_selectors = 'a[rel="next"], a[aria-label*="Next"], a[aria-label*="next"], button[aria-label*="Next"], button[aria-label*="next"], li.next a'
                    next_button = driver.find_element(By.CSS_SELECTOR, css_selectors)
                    
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    time.sleep(2)
                    driver.execute_script("arguments[0].click();", next_button)
                    
                    self.stdout.write(self.style.WARNING(f'Clicked Next! Loading Page {current_page + 1}...'))
                    time.sleep(6) 
                    
                    # 2. حماية الدوران: نتحقق من الرابط الجديد بعد الضغط
                    current_url = driver.current_url
                    
                    # إذا كان الرابط لم يتغير، أو اكتشفنا أن الموقع أعادنا للصفحة الأولى (offset=0)
                    if current_url == previous_url or "offset=0" in current_url:
                        self.stdout.write(self.style.SUCCESS('\n🏁 Reached the end (Site looped back). Stopping safely!'))
                        break # نكسر الحلقة ونتوقف

                    current_page += 1
                except Exception as e:
                    self.stdout.write(self.style.SUCCESS('\n🏁 No more "Next" button found. We reached the LAST PAGE!'))
                    break
                    
            self.stdout.write(self.style.SUCCESS(f'\n🎉 FULL HARVEST COMPLETE! Successfully scraped and linked {added_count} new programs.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
        finally:
            time.sleep(3)
            if 'driver' in locals():
                driver.quit()