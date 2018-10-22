from django.contrib import admin
import csv
from django.http import HttpResponse
from .models import( Profile,
                    AnswerPaper,
                    Question
                   )

try:
    from StringIO import StringIO as string_io
except ImportError:
    from io import BytesIO as string_io


class ProfileAdmin(admin.ModelAdmin):
	list_display = ['title','user', 'institute', 
					'phone_number','position']


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question', 'correct_answer', 'question_day']



class AnswerPaperAdmin(admin.ModelAdmin):
    list_display = ['participant', 'answered_q', 'date']
    actions = ['download_csv']

    def download_csv(self, request, queryset):
        openfile = string_io() 
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;\
										filename=AnswerPaper_data.csv'
                                        
        writer = csv.writer(response)
        writer.writerow(['Participant', 'Answer date/time'])
        for q in queryset:
            writer.writerow([q.participant.user.get_full_name(), q.date])
    
        openfile.seek(0)
        response.write(openfile.read())
        return response
	
    download_csv.short_description = "Download CSV file for selected stats."



# Register your models here.
admin.site.register(Profile, ProfileAdmin)
admin.site.register(AnswerPaper, AnswerPaperAdmin)
admin.site.register(Question, QuestionAdmin)