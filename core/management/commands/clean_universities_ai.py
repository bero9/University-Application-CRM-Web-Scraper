import os
import json
from google import genai
from dotenv import load_dotenv # إضافة هذه المكتبة
from django.core.management.base import BaseCommand
from core.models import University, Program

class Command(BaseCommand):
    help = 'Clean and merge duplicate German universities using Gemini AI'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting AI Data Cleaner... 🤖🧹'))

        # تحميل المتغيرات المخفية
        load_dotenv()

        # جلب المفتاح بأمان
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 

        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to initialize Gemini Client: {e}'))
            return

        # === 2. جلب جميع أسماء الجامعات ===
        universities = list(University.objects.values_list('name', flat=True))
        
        if not universities:
            self.stdout.write(self.style.ERROR('No universities found in the database.'))
            return
            
        self.stdout.write(self.style.WARNING(f'Sending {len(universities)} universities to Gemini for analysis...'))

        # === 3. هندسة الأوامر (Prompt Engineering) ===
        prompt = f"""
        You are an expert Data Engineer specializing in German universities.
        I have a list of university names scraped from the web. Some are duplicates, abbreviations, or variants of the same institution.
        
        Analyze this list and group the duplicates together under their full, official English name.
        
        Return ONLY a valid JSON array of objects. Do not write any markdown blocks like ```json or any other conversational text. Just the raw JSON.
        Format MUST exactly match this:
        [
            {{
                "official_name": "Technical University of Munich",
                "duplicates": ["TU Munich", "Technical University Munich", "TUM", "Technical University of Munich"]
            }},
            {{
                "official_name": "RWTH Aachen University",
                "duplicates": ["RWTH Aachen"]
            }}
        ]
        
        If a university has no duplicates and its name is totally fine and standalone, DO NOT include it in the JSON. ONLY include groups that have variants or need renaming.
        
        Here is the list of universities:
        {json.dumps(universities)}
        """

        try:
            # === 4. إرسال الطلب بالطريقة الحديثة ===
            self.stdout.write(self.style.NOTICE('Waiting for Gemini to think... 🤔'))
            
            response = client.models.generate_content(
                model='gemini-3.6-flash', # تم التحديث للنسخة الأحدث المطلوبة!
                contents=prompt,
            )
            
            # تنظيف النص
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
                
            mappings = json.loads(response_text)
            
            self.stdout.write(self.style.SUCCESS(f'Gemini found {len(mappings)} groups of duplicates! Starting the merge process...'))
            
            # === 5. عملية الدمج ===
            merged_count = 0
            
            for group in mappings:
                official_name = group.get('official_name')
                duplicates = group.get('duplicates', [])
                
                if not official_name or not duplicates:
                    continue
                    
                official_uni, created = University.objects.get_or_create(
                    name=official_name, 
                    defaults={'country': 'Germany'}
                )
                
                for dup_name in duplicates:
                    if dup_name == official_name:
                        continue
                        
                    dup_uni = University.objects.filter(name=dup_name).first()
                    
                    if dup_uni:
                        programs_to_update = Program.objects.filter(university=dup_uni)
                        prog_count = programs_to_update.count()
                        
                        programs_to_update.update(university=official_uni)
                        dup_uni.delete()
                        
                        merged_count += 1
                        self.stdout.write(self.style.SUCCESS(f'  [+] Merged "{dup_name}" ({prog_count} programs) -> "{official_name}"'))
                        
            self.stdout.write(self.style.SUCCESS(f'\n🎉 AI Cleanup Complete! Merged and deleted {merged_count} duplicate universities.'))

        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Gemini did not return valid JSON. Here is what it said instead:'))
            self.stdout.write(response.text)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An AI processing error occurred: {e}'))