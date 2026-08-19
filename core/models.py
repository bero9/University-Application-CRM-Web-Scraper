import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    نموذج المستخدم المخصص للطلاب. 
    نستخدم UUID بدلاً من الأرقام التسلسلية لزيادة الأمان.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # الحقول الأساسية مثل email و username و password موجودة مسبقاً في AbstractUser
    
    def __str__(self):
        return self.username

class University(models.Model):
    """
    جدول الجامعات الذي سيتم تعبئته بواسطة الـ Scraper
    """
    name = models.CharField(max_length=255, verbose_name="اسم الجامعة")
    country = models.CharField(max_length=100, verbose_name="الدولة")
    ranking = models.IntegerField(null=True, blank=True, verbose_name="التصنيف العالمي")
    website_url = models.URLField(max_length=500, verbose_name="الرابط الرسمي")
    scraped_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ آخر تحديث")

    class Meta:
        verbose_name_plural = "Universities"

    def __str__(self):
        return f"{self.name} - {self.country}"

class Program(models.Model):
    """
    جدول البرامج الدراسية المرتبطة بالجامعات
    """
    DEGREE_CHOICES = [
        ('Bachelor', 'بكالوريوس'),
        ('Master', 'ماجستير'),
        ('PhD', 'دكتوراه'),
    ]

    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='programs', verbose_name="الجامعة")
    title = models.CharField(max_length=255, verbose_name="اسم التخصص")
    degree_level = models.CharField(max_length=50, choices=DEGREE_CHOICES, verbose_name="الدرجة العلمية")
    language = models.CharField(max_length=50, verbose_name="لغة التدريس")
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="الرسوم الدراسية")
    deadline = models.DateField(null=True, blank=True, verbose_name="موعد التقديم")
    program_url = models.URLField(max_length=500, verbose_name="رابط تفاصيل البرنامج")

    def __str__(self):
        return f"{self.title} ({self.degree_level}) - {self.university.name}"

class Requirement(models.Model):
    """
    متطلبات كل برنامج دراسي (مثل IELTS, GPA, إلخ)
    """
    REQ_TYPE_CHOICES = [
        ('GPA', 'المعدل التراكمي'),
        ('Language', 'اختبار لغة (IELTS/TOEFL)'),
        ('Test', 'اختبار قبول (GRE/GMAT)'),
        ('Experience', 'خبرة عمل'),
        ('Other', 'أخرى'),
    ]

    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='requirements', verbose_name="البرنامج الدراسي")
    req_type = models.CharField(max_length=50, choices=REQ_TYPE_CHOICES, verbose_name="نوع الشرط")
    description = models.TextField(verbose_name="التفاصيل")

    def __str__(self):
        return f"{self.get_req_type_display()} - {self.program.title}"

class Application(models.Model):
    """
    جدول طلبات التقديم الذي يربط الطالب بالبرنامج المختار لتتبع حالته
    """
    STATUS_CHOICES = [
        ('Preparing', 'قيد التجهيز'),
        ('Submitted', 'تم الإرسال'),
        ('In Review', 'قيد المراجعة'),
        ('Accepted', 'مقبول'),
        ('Rejected', 'مرفوض'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications', verbose_name="الطالب")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='applications', verbose_name="البرنامج الدراسي")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Preparing', verbose_name="حالة الطلب")
    custom_deadline = models.DateField(null=True, blank=True, verbose_name="تاريخ الاستحقاق الشخصي")
    notes = models.TextField(null=True, blank=True, verbose_name="ملاحظات شخصية")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Application: {self.user.username} -> {self.program.title} ({self.get_status_display()})"

class Document(models.Model):
    """
    الملفات التي يرفعها الطالب لكل طلب تقديم (مثل CV، رسالة الدوافع)
    """
    DOC_TYPE_CHOICES = [
        ('CV', 'سيرة ذاتية'),
        ('Motivation Letter', 'رسالة دوافع'),
        ('Transcript', 'كشف درجات'),
        ('Passport', 'جواز سفر'),
        ('Other', 'أخرى'),
    ]

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents', verbose_name="طلب التقديم")
    file_name = models.CharField(max_length=255, verbose_name="اسم الملف")
    doc_type = models.CharField(max_length=50, choices=DOC_TYPE_CHOICES, verbose_name="نوع الملف")
    file = models.FileField(upload_to='application_docs/%Y/%m/%d/', verbose_name="الملف المرفوع")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_doc_type_display()} for {self.application.program.title}"